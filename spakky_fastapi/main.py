from spakky.application.application import SpakkyApplication

from spakky_fastapi.post_processors.add_builtin_middlewares import (
    AddBuiltInMiddlewaresPostProcessor,
)
from spakky_fastapi.post_processors.register_routes import RegisterRoutesPostProcessor


def initialize(app: SpakkyApplication) -> None:
    app.add(AddBuiltInMiddlewaresPostProcessor)
    app.add(RegisterRoutesPostProcessor)
