from logging import Logger

from fastapi import FastAPI
from spakky.application.application_context import ApplicationContext
from spakky.application.interfaces.pluggable import IPluggable

from spakky_fastapi.plugins.fast_api import FastAPIPlugin
from spakky_fastapi.post_processor import FastAPIPostProcessor


def test_fast_api_plugin_register(logger: Logger) -> None:
    app: FastAPI = FastAPI(debug=True)
    context: ApplicationContext = ApplicationContext()
    plugin: IPluggable = FastAPIPlugin(app, logger)
    plugin.register(context)

    assert context.post_processors == {FastAPIPostProcessor}
