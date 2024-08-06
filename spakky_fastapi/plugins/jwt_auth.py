from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.registry import IRegistry

from spakky_fastapi.aspects.jwt_auth import AsyncJWTAuthAdvisor, JWTAuthAdvisor


class JWTAuthPlugin(IPluggable):
    def register(self, registry: IRegistry) -> None:
        registry.register_bean(JWTAuthAdvisor)
        registry.register_bean(AsyncJWTAuthAdvisor)
