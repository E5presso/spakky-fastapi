from spakky.application.application_context import ApplicationContext
from spakky.application.interfaces.pluggable import IPluggable

from spakky_fastapi.aspects.authenticate import (
    AsyncAuthenticationAspect,
    AuthenticationAspect,
)
from spakky_fastapi.plugins.authenticate import AuthenticatePlugin


def test_jwt_auth_plugin_register() -> None:
    context: ApplicationContext = ApplicationContext()
    plugin: IPluggable = AuthenticatePlugin()
    plugin.register(context)

    assert context.pods == {AuthenticationAspect, AsyncAuthenticationAspect}
