from dataclasses import asdict
from functools import wraps
from inspect import getmembers, signature
from logging import Logger
from typing import Any

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import FastAPIError
from fastapi.utils import create_model_field  # type: ignore
from spakky.pod.annotations.order import Order
from spakky.pod.annotations.pod import Pod
from spakky.pod.interfaces.aware.container_aware import IContainerAware
from spakky.pod.interfaces.aware.logger_aware import ILoggerAware
from spakky.pod.interfaces.container import IContainer
from spakky.pod.interfaces.post_processor import IPostProcessor

from spakky_fastapi.routes.route import Route
from spakky_fastapi.routes.websocket import WebSocketRoute
from spakky_fastapi.stereotypes.api_controller import ApiController


@Order(0)
@Pod()
class RegisterRoutesPostProcessor(IPostProcessor, ILoggerAware, IContainerAware):
    __logger: Logger
    __container: IContainer

    def set_logger(self, logger: Logger) -> None:
        self.__logger = logger

    def set_container(self, container: IContainer) -> None:
        self.__container = container

    def post_process(self, pod: object) -> object:
        if not ApiController.exists(pod):
            return pod

        fast_api = self.__container.get(FastAPI)
        controller = ApiController.get(pod)
        router: APIRouter = APIRouter(prefix=controller.prefix, tags=controller.tags)
        for name, method in getmembers(pod, callable):
            route: Route | None = Route.get_or_none(method)
            websocket_route: WebSocketRoute | None = WebSocketRoute.get_or_none(method)
            if route is None and websocket_route is None:
                continue

            if route is not None:
                # pylint: disable=line-too-long
                self.__logger.debug(
                    f"[{type(self).__name__}] {route.methods!r} {controller.prefix}{route.path} -> {method.__qualname__}"
                )
                if route.name is None:
                    route.name = " ".join([x.capitalize() for x in name.split("_")])
                if route.description is None:
                    route.description = method.__doc__
                if route.response_model is None:
                    return_annotation: type | None = signature(method).return_annotation
                    if return_annotation is not None:
                        try:
                            create_model_field("", return_annotation)
                            route.response_model = return_annotation
                        except FastAPIError:
                            pass

                @wraps(method)
                async def endpoint(
                    *args: Any,
                    method_name: str = name,
                    controller_type: type[object] = controller.type_,
                    context: IContainer = self.__container,
                    **kwargs: Any,
                ) -> Any:
                    controller_instance = context.get(controller_type)
                    method_to_call = getattr(controller_instance, method_name)
                    return await method_to_call(*args, **kwargs)

                router.add_api_route(endpoint=endpoint, **asdict(route))
            if websocket_route is not None:
                # pylint: disable=line-too-long
                self.__logger.debug(
                    f"[{type(self).__name__}] [WebSocket] {controller.prefix}{websocket_route.path} -> {method.__qualname__}"
                )
                if websocket_route.name is None:
                    websocket_route.name = " ".join(
                        [x.capitalize() for x in name.split("_")]
                    )

                @wraps(method)
                async def websocket_endpoint(
                    *args: Any,
                    method_name: str = name,
                    controller_type: type[object] = controller.type_,
                    context: IContainer = self.__container,
                    **kwargs: Any,
                ) -> Any:
                    controller_instance = context.get(controller_type)
                    method_to_call = getattr(controller_instance, method_name)
                    return await method_to_call(*args, **kwargs)

                router.add_api_websocket_route(
                    endpoint=websocket_endpoint, **asdict(websocket_route)
                )
        fast_api.include_router(router)
        return pod
