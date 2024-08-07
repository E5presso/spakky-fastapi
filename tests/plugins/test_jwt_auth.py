from spakky.application.application_context import ApplicationContext
from spakky.application.interfaces.pluggable import IPluggable

from spakky_fastapi.extensions.auth import (
    AsyncAuthenticationAdvisor,
    AuthenticationAdvisor,
)
from spakky_fastapi.plugins.jwt_auth import JWTAuthPlugin


def test_jwt_auth_plugin_register() -> None:
    context: ApplicationContext = ApplicationContext()
    plugin: IPluggable = JWTAuthPlugin()
    plugin.register(context)

    assert context.beans == {AuthenticationAdvisor, AsyncAuthenticationAdvisor}
