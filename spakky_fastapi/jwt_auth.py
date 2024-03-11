from typing import Any, TypeVar, Protocol, Awaitable, runtime_checkable
from inspect import signature
from logging import Logger
from dataclasses import InitVar, field, dataclass

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from spakky.aop.advice import Around
from spakky.aop.advisor import IAsyncAdvisor
from spakky.aop.aspect import AsyncAspect
from spakky.aop.error import SpakkyAOPError
from spakky.aop.order import Order
from spakky.bean.autowired import autowired
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFunc, P
from spakky.cryptography.error import InvalidJWTFormatError, JWTDecodingError
from spakky.cryptography.jwt import JWT
from spakky.cryptography.key import Key
from spakky_fastapi.error import Unauthorized

R_co = TypeVar("R_co", covariant=True)


class AuthenticationFailedError(SpakkyAOPError):
    message = "사용자 인증에 실패했습니다."


@runtime_checkable
class IAuthenticatedFunction(Protocol[P, R_co]):
    __defaults__: tuple[Any, ...] | None
    __kwdefaults__: dict[str, Any] | None

    # pylint: disable=no-self-argument
    def __call__(
        self_,  # type: ignore
        self: Any,
        token: JWT,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> Awaitable[R_co]:
        raise NotImplementedError


@dataclass
class JWTAuth(FunctionAnnotation):
    token_url: InitVar[str]
    authenticator: OAuth2PasswordBearer = field(init=False)

    def __post_init__(self, token_url: str) -> None:
        self.authenticator = OAuth2PasswordBearer(tokenUrl=token_url)

    def __call__(
        self, obj: IAuthenticatedFunction[P, R_co]
    ) -> IAuthenticatedFunction[P, R_co]:
        parameters = list(signature(obj).parameters.values())
        if obj.__defaults__ is not None:
            extra = obj.__defaults__
        else:
            extra = tuple(Depends() for x in parameters[1:] if x.name != "token")
        obj.__defaults__ = (Depends(self.authenticator),) + extra
        return super().__call__(obj)


@Order(1)
@AsyncAspect()
class AsyncJWTAuthAdvisor(IAsyncAdvisor):
    __logger: Logger
    __key: Key

    @autowired
    def __init__(self, logger: Logger, key: Key) -> None:
        super().__init__()
        self.__logger = logger
        self.__key = key

    @Around(JWTAuth.contains)
    async def around_async(self, joinpoint: AsyncFunc, *args: Any, **kwargs: Any) -> Any:
        token: str = kwargs["token"]
        try:
            jwt: JWT = JWT(token=token)
        except (InvalidJWTFormatError, JWTDecodingError) as e:
            raise Unauthorized(AuthenticationFailedError()) from e
        if jwt.is_expired:
            raise Unauthorized(AuthenticationFailedError())
        if jwt.verify(self.__key) is False:
            raise Unauthorized(AuthenticationFailedError())
        self.__logger.info(f"[{type(self).__name__}] {jwt.payload!r}")
        kwargs["token"] = jwt
        return await joinpoint(*args, **kwargs)
