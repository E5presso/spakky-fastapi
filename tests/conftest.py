import logging
from typing import Any, Generator
from logging import Logger, Formatter, StreamHandler, getLogger

import pytest
from fastapi import FastAPI
from spakky.application.application_context import ApplicationContext
from spakky.plugins.aspect import AspectPlugin
from spakky.plugins.logging import LoggingPlugin
from spakky.pod.pod import Pod
from spakky.security.key import Key

from spakky_fastapi.middlewares.error_handling import ErrorHandlingMiddleware
from spakky_fastapi.plugins.authenticate import AuthenticatePlugin
from spakky_fastapi.plugins.fast_api import FastAPIPlugin
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
    @Pod(name="logger")
    def get_logger() -> Logger:
        return logger

    @Pod(name="key")
    def get_key() -> Key:
        return key

    app: FastAPI = FastAPI(debug=True)
    app.add_middleware(ErrorHandlingMiddleware, debug=True)
    context: ApplicationContext = ApplicationContext(package=apps)

    context.register_plugin(LoggingPlugin())
    context.register_plugin(AuthenticatePlugin())
    context.register_plugin(FastAPIPlugin(app, logger))
    context.register_plugin(AspectPlugin(logger))

    context.register(get_logger)
    context.register(get_key)

    context.start()
    yield app
