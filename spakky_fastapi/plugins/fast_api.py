from logging import Logger

from fastapi import FastAPI
from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.registry import IRegistry

from spakky_fastapi.post_processor import FastAPIBeanPostProcessor


class FastAPIPlugin(IPluggable):
    app: FastAPI
    logger: Logger

    def __init__(self, app: FastAPI, logger: Logger) -> None:
        self.app = app
        self.logger = logger

    def register(self, registry: IRegistry) -> None:
        registry.register_bean_post_processor(
            FastAPIBeanPostProcessor(
                self.app,
                self.logger,
            )
        )
