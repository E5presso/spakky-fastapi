from enum import Enum
from dataclasses import dataclass

from spakky.stereotype.controller import Controller


@dataclass
class ApiController(Controller):
    tags: list[str | Enum] | None = None
