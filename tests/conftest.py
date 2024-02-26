import logging
from typing import Any, Generator
from logging import Logger, Formatter, StreamHandler, getLogger

import pytest
from fastapi import FastAPI
from spakky.bean.application_context import ApplicationContext
from spakky_fastapi.post_processor import FastAPIBeanPostProcessor

from tests import apps


@pytest.fixture(name="logger", scope="function")
def get_logger_fixture() -> Generator[Logger, Any, None]:
    logger: Logger = getLogger("simple_example")  # type: ignore
    logger.setLevel(logging.DEBUG)
    console = StreamHandler()
    console.setLevel(level=logging.DEBUG)
    formatter = Formatter("[%(levelname)s] (%(asctime)s) : %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)
    yield logger


@pytest.fixture(name="app", scope="function")
def get_app_fixture(logger: Logger) -> Generator[FastAPI, Any, None]:
    app: FastAPI = FastAPI()
    context: ApplicationContext = ApplicationContext(apps)
    context.register_bean_post_processor(FastAPIBeanPostProcessor(app, logger))
    context.start()
    yield app
