import logging
from logging import Formatter, StreamHandler, getLogger
from typing import Any, AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from spakky.application.application import SpakkyApplication
from spakky.application.application_context import ApplicationContext
from spakky.pod.annotations.pod import Pod
from spakky.security.key import Key

from tests import apps


@pytest.fixture(name="key", scope="session")
def get_key_fixture() -> Generator[Key, Any, None]:
    key: Key = Key(size=32)
    yield key


@pytest.mark.asyncio
@pytest.fixture(name="app", scope="function")
async def get_app_fixture(key: Key) -> AsyncGenerator[FastAPI, Any]:
    logger = getLogger("debug")
    logger.setLevel(logging.DEBUG)
    console = StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger.addHandler(console)

    @Pod(name="key")
    def get_key() -> Key:
        return key

    @Pod(name="api")
    def get_api() -> FastAPI:
        return FastAPI(debug=True)

    app = (
        SpakkyApplication(ApplicationContext(logger))
        .load_plugins()
        .enable_async_logging()
        .enable_logging()
        .scan(apps)
        .add(get_key)
        .add(get_api)
    )
    app.start()

    yield app.container.get(type_=FastAPI)

    app.stop()
    logger.removeHandler(console)
