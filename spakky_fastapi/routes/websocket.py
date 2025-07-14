from dataclasses import dataclass
from typing import Any, Callable, Sequence, TypeAlias

from fastapi import params
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import FuncT

SetIntStr: TypeAlias = set[int | str]
DictIntStrAny: TypeAlias = dict[int | str, Any]


@dataclass
class WebSocketRoute(FunctionAnnotation):
    path: str
    name: str | None = None
    dependencies: Sequence[params.Depends] | None = None


def websocket(
    path: str,
    name: str | None = None,
    dependencies: Sequence[params.Depends] | None = None,
) -> Callable[[FuncT], FuncT]:
    return WebSocketRoute(
        path=path,
        name=name,
        dependencies=dependencies,
    )
