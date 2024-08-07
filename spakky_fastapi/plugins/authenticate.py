from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.registry import IRegistry

from spakky_fastapi.extensions.authenticate import (
    AsyncAuthenticationAdvisor,
    AuthenticationAdvisor,
)


class AuthenticatePlugin(IPluggable):
    def register(self, registry: IRegistry) -> None:
        registry.register_bean(AuthenticationAdvisor)
        registry.register_bean(AsyncAuthenticationAdvisor)
