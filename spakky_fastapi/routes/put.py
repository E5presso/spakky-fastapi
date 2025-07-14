from typing import Any, Callable, Sequence

from fastapi import Response, params
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from spakky.core.types import FuncT
from starlette.routing import Route as StarletteRoute

from spakky_fastapi.routes.route import DictIntStrAny, HTTPMethod, SetIntStr, route


def put(
    path: str,
    response_model: type[Any] | None = None,
    status_code: int | None = None,
    tags: list[str] | None = None,
    dependencies: Sequence[params.Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    operation_id: str | None = None,
    response_model_include: SetIntStr | DictIntStrAny | None = None,
    response_model_exclude: SetIntStr | DictIntStrAny | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] = JSONResponse,
    name: str | None = None,
    route_class_override: type[APIRoute] | None = None,
    callbacks: list[StarletteRoute] | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[FuncT], FuncT]:
    return route(
        path=path,
        methods=[HTTPMethod.PUT],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        route_class_override=route_class_override,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
    )
