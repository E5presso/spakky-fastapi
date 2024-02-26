from typing import Any
from inspect import signature, getmembers
from logging import Logger
from dataclasses import asdict

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import FastAPIError
from fastapi.utils import create_response_field  # type: ignore
from spakky.bean.interfaces.bean_container import IBeanContainer
from spakky.bean.interfaces.post_processor import IBeanPostProcessor
from spakky.stereotype.controller import Controller
from spakky_fastapi.routing import Route


class FastAPIBeanPostProcessor(IBeanPostProcessor):
    __app: FastAPI
    __logger: Logger

    def __init__(self, app: FastAPI, logger: Logger) -> None:
        super().__init__()
        self.__app = app
        self.__logger = logger

    def post_process_bean(self, container: IBeanContainer, bean: Any) -> Any:
        if Controller.contains(bean):
            controller = Controller.single(bean)
            router: APIRouter = APIRouter(prefix=controller.prefix)
            methods = getmembers(bean, Route.contains)
            for name, method in methods:
                route = Route.single(method)
                self.__logger.info(
                    f"[{type(self).__name__}] {route.methods} {controller.prefix}{route.path} -> {method.__qualname__}"
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
            self.__app.include_router(router)
        return bean
