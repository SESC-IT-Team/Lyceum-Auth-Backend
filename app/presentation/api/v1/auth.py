from sesc_auth_sdk.routers.auth_router import create_auth_router

from app.config import settings

router = create_auth_router(settings.auth_router_settings)