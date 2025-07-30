from typing import Any

from edgy.conf import settings
from edgy.contrib.admin import create_admin_app
from lilya.apps import Lilya
from lilya.middleware import DefineMiddleware
from lilya.middleware.sessions import SessionMiddleware
from lilya.routing import Include


def get_admin_application() -> Any:
    admin_app = create_admin_app()
    routes = [
        Include(
            path="/admin",
            app=admin_app,
        ),
    ]
    app: Any = Lilya(
        routes=routes,
        middleware=[
            # you can also use a different secret_key aside from settings.admin_config.SECRET_KEY
            DefineMiddleware(SessionMiddleware, secret_key=settings.admin_config.SECRET_KEY),
        ],
    )
    return app


