from typing import Any, TypeVar, Callable, Annotated, Awaitable, TypeAlias, Concatenate
from inspect import iscoroutinefunction
from logging import Logger
from dataclasses import InitVar, field, dataclass

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from spakky.aop.advice import Around
from spakky.aop.advisor import IAdvisor, IAsyncAdvisor
from spakky.aop.aspect import Aspect, AsyncAspect
from spakky.aop.error import SpakkyAOPError
from spakky.aop.order import Order
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFunc, Func, P
from spakky.cryptography.error import InvalidJWTFormatError, JWTDecodingError
from spakky.cryptography.jwt import JWT
from spakky.cryptography.key import Key

from spakky_fastapi.error import Unauthorized

R_co = TypeVar("R_co", covariant=True)


class AuthenticationFailedError(SpakkyAOPError):
    message = "사용자 인증에 실패했습니다."


IAuthenticatedFunction: TypeAlias = (
    Callable[Concatenate[Any, JWT, P], R_co]
    | Callable[Concatenate[Any, JWT, P], Awaitable[R_co]]
)


@dataclass
class Auth(FunctionAnnotation):
    token_url: InitVar[str]
    authenticator: OAuth2PasswordBearer = field(init=False)
    token_keywords: list[str] = field(init=False, default_factory=list)

    def __post_init__(self, token_url: str) -> None:
        self.authenticator = OAuth2PasswordBearer(tokenUrl=token_url)

    def __call__(
        self, obj: IAuthenticatedFunction[P, R_co]
    ) -> IAuthenticatedFunction[P, R_co]:
        for key, value in obj.__annotations__.items():
            if value == JWT:
                obj.__annotations__[key] = Annotated[JWT, Depends(self.authenticator)]
                self.token_keywords.append(key)
        return super().__call__(obj)


@Order(1)
@Aspect()
class AuthenticationAdvisor(IAdvisor):
    __logger: Logger
    __key: Key

    def __init__(self, logger: Logger, key: Key) -> None:
        super().__init__()
        self.__logger = logger
        self.__key = key

    @Around(lambda x: Auth.contains(x) and not iscoroutinefunction(x))
    def around(self, joinpoint: Func, *args: Any, **kwargs: Any) -> Any:
        annotation: Auth = Auth.single(joinpoint)
        for keyword in annotation.token_keywords:
            token: str = kwargs[keyword]
            try:
                jwt: JWT = JWT(token=token)
            except (InvalidJWTFormatError, JWTDecodingError) as e:
                raise Unauthorized(AuthenticationFailedError()) from e
            if jwt.is_expired:
                raise Unauthorized(AuthenticationFailedError())
            if jwt.verify(self.__key) is False:
                raise Unauthorized(AuthenticationFailedError())
            self.__logger.info(f"[{type(self).__name__}] {jwt.payload!r}")
            kwargs[keyword] = jwt
        return joinpoint(*args, **kwargs)


@Order(1)
@AsyncAspect()
class AsyncAuthenticationAdvisor(IAsyncAdvisor):
    __logger: Logger
    __key: Key

    def __init__(self, logger: Logger, key: Key) -> None:
        super().__init__()
        self.__logger = logger
        self.__key = key

    @Around(lambda x: Auth.contains(x) and iscoroutinefunction(x))
    async def around_async(self, joinpoint: AsyncFunc, *args: Any, **kwargs: Any) -> Any:
        annotation: Auth = Auth.single(joinpoint)
        for keyword in annotation.token_keywords:
            token: str = kwargs[keyword]
            try:
                jwt: JWT = JWT(token=token)
            except (InvalidJWTFormatError, JWTDecodingError) as e:
                raise Unauthorized(AuthenticationFailedError()) from e
            if jwt.is_expired:
                raise Unauthorized(AuthenticationFailedError())
            if jwt.verify(self.__key) is False:
                raise Unauthorized(AuthenticationFailedError())
            self.__logger.info(f"[{type(self).__name__}] {jwt.payload!r}")
            kwargs[keyword] = jwt
        return await joinpoint(*args, **kwargs)
