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
from spakky_fastapi.post_processor import FastAPIBeanPostProcessor

from tests import apps


@pytest.fixture(name="key", scope="session")
def get_key_fixture() -> Generator[Key, Any, None]:
    key: Key = Key(size=32)
    yield key


@pytest.fixture(name="app", scope="function")
def get_app_fixture(key: Key) -> Generator[FastAPI, Any, None]:
    logger: Logger = getLogger("debug")
    logger.setLevel(logging.DEBUG)
    console = StreamHandler()
    console.setLevel(level=logging.DEBUG)
    formatter = Formatter("[%(levelname)s] (%(asctime)s) : %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)

    @BeanFactory()
    def get_logger() -> Logger:
        return logger

    @BeanFactory()
    def get_key() -> Key:
        return key

    app: FastAPI = FastAPI()
    context: ApplicationContext = ApplicationContext(apps)
    context.register_bean_factory(get_logger)
    context.register_bean_factory(get_key)
    context.register_bean(AsyncLoggingAdvisor)
    context.register_bean(AsyncJWTAuthAdvisor)
    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean_post_processor(FastAPIBeanPostProcessor(app, logger))
    context.start()
    yield app

    logger.removeHandler(console)
