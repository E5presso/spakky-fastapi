import logging
from typing import Any, Generator
from logging import Logger, Formatter, StreamHandler, getLogger

import pytest
from fastapi import FastAPI
from spakky.aop.post_processor import AspectBeanPostProcessor
from spakky.bean.application_context import ApplicationContext
from spakky.bean.bean import BeanFactory
from spakky.extensions.logging import AsyncLoggingAdvisor
from spakky_fastapi.post_processor import FastAPIBeanPostProcessor

from tests import apps


@BeanFactory()
def get_logger() -> Logger:
    logger: Logger = getLogger("debug")
    logger.setLevel(logging.DEBUG)
    console = StreamHandler()
    console.setLevel(level=logging.DEBUG)
    formatter = Formatter("[%(levelname)s] (%(asctime)s) : %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger


@pytest.fixture(name="app", scope="session")
def get_app_fixture() -> Generator[FastAPI, Any, None]:
    app: FastAPI = FastAPI()
    context: ApplicationContext = ApplicationContext(apps)
    context.register_bean(AsyncLoggingAdvisor)
    context.register_bean_factory(get_logger)
    logger: Logger = context.single(required_type=Logger)
    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean_post_processor(FastAPIBeanPostProcessor(app, logger))
    context.start()
    yield app
