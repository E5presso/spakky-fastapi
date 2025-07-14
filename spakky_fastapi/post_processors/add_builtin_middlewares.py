from fastapi import FastAPI
from spakky.pod.annotations.order import Order
from spakky.pod.annotations.pod import Pod
from spakky.pod.interfaces.application_context import IApplicationContext
from spakky.pod.interfaces.aware.application_context_aware import (
    IApplicationContextAware,
)
from spakky.pod.interfaces.post_processor import IPostProcessor

from spakky_fastapi.middlewares.error_handling import ErrorHandlingMiddleware
from spakky_fastapi.middlewares.manage_context import ManageContextMiddleware


@Order(0)
@Pod()
class AddBuiltInMiddlewaresPostProcessor(IPostProcessor, IApplicationContextAware):
    __application_context: IApplicationContext

    def set_application_context(self, application_context: IApplicationContext) -> None:
        self.__application_context = application_context

    def post_process(self, pod: object) -> object:
        if not isinstance(pod, FastAPI):
            return pod

        pod.add_middleware(
            ErrorHandlingMiddleware,
            debug=pod.debug,
        )
        pod.add_middleware(
            ManageContextMiddleware,
            application_context=self.__application_context,
        )
        return pod
