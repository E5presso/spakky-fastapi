import logging
from typing import Any, Generator
from logging import Logger, Formatter, StreamHandler, getLogger

import pytest
from fastapi import FastAPI
from spakky.aop.post_processor import AspectBeanPostProcessor
from spakky.bean.application_context import ApplicationContext
from spakky.bean.bean import BeanFactory
from spakky.cryptography.key import Key
from spakky.extensions.logging import AsyncLoggingAdvisor
from spakky_fastapi.jwt_auth import AsyncJWTAuthAdvisor
from spakky_fastapi.middlewares.error_handling import ErrorHandlingMiddleware
from spakky_fastapi.post_processor import FastAPIBeanPostProcessor

from tests import apps


@pytest.fixture(name="key", scope="session")
def get_key_fixture() -> Generator[Key, Any, None]:
    key: Key = Key(size=32)
    yield key


@pytest.fixture(name="logger", scope="session")
def get_logger_fixture() -> Generator[Logger, Any, None]:
    logger: Logger = getLogger("debug")
    logger.setLevel(logging.DEBUG)
    console = StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(Formatter("[%(levelname)s] (%(asctime)s) : %(message)s"))
    logger.addHandler(console)

    yield logger

    logger.removeHandler(console)


@pytest.fixture(name="app", scope="function")
def get_app_fixture(key: Key, logger: Logger) -> Generator[FastAPI, Any, None]:
    @BeanFactory()
    def get_logger() -> Logger:
        return logger

    @BeanFactory()
    def get_key() -> Key:
        return key

    app: FastAPI = FastAPI(debug=True)
    app.add_middleware(ErrorHandlingMiddleware, debug=True)
    context: ApplicationContext = ApplicationContext(apps)
    context.register_bean_factory(get_logger)
    context.register_bean_factory(get_key)
    context.register_bean(AsyncLoggingAdvisor)
    context.register_bean(AsyncJWTAuthAdvisor)
    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean_post_processor(FastAPIBeanPostProcessor(app, logger))
    context.start()
    yield app
