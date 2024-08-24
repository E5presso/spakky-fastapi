from inspect import signature, getmembers
from logging import Logger
from dataclasses import asdict

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import FastAPIError
from fastapi.utils import create_response_field  # type: ignore
from spakky.application.interfaces.container import IPodContainer
from spakky.application.interfaces.post_processor import IPodPostProcessor
from spakky.pod.order import Order

from spakky_fastapi.stereotypes.api_controller import (
    ApiController,
    Route,
    WebSocketRoute,
)


@Order(1)
class FastAPIPostProcessor(IPodPostProcessor):
    __app: FastAPI
    __logger: Logger

    def __init__(self, app: FastAPI, logger: Logger) -> None:
        super().__init__()
        self.__app = app
        self.__logger = logger

    def post_process(self, container: IPodContainer, pod: object) -> object:
        if not ApiController.exists(pod):
            return pod
        controller = ApiController.get(pod)
        router: APIRouter = APIRouter(prefix=controller.prefix, tags=controller.tags)
        for name, method in getmembers(pod, callable):
            route: Route | None = Route.get_or_none(method)
            websocket_route: WebSocketRoute | None = WebSocketRoute.get_or_none(method)
            if route is None and websocket_route is None:
                continue
            if route is not None:
                # pylint: disable=line-too-long
                self.__logger.info(
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
                            create_response_field("", return_annotation)
                        except FastAPIError:
                            pass
                        else:
                            route.response_model = return_annotation
                router.add_api_route(endpoint=method, **asdict(route))
            if websocket_route is not None:
                # pylint: disable=line-too-long
                self.__logger.info(
                    f"[{type(self).__name__}] [WebSocket] {controller.prefix}{websocket_route.path} -> {method.__qualname__}"
                )
                if websocket_route.name is None:
                    websocket_route.name = " ".join(
                        [x.capitalize() for x in name.split("_")]
                    )
                router.add_api_websocket_route(endpoint=method, **asdict(websocket_route))
        self.__app.include_router(router)
        return pod
