from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.registry import IPodRegistry

from spakky_fastapi.aspects.authenticate import (
    AsyncAuthenticationAspect,
    AuthenticationAspect,
)


class AuthenticatePlugin(IPluggable):
    def register(self, registry: IPodRegistry) -> None:
        registry.register(AuthenticationAspect)
        registry.register(AsyncAuthenticationAspect)
