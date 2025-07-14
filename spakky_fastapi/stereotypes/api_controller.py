from dataclasses import dataclass
from enum import Enum

from spakky.stereotype.controller import Controller


@dataclass(eq=False)
class ApiController(Controller):
    prefix: str
    tags: list[str | Enum] | None = None
