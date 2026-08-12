import asyncio

from sesc_auth_sdk.enums.gender import Gender
from sesc_auth_sdk.enums.role import Role

from app.application.services.authentik_service import AuthentikService
from app.application.services.user_service import UserService
from app.config import settings
from app.infrastructure.database import async_session_factory
from app.infrastructure.repositories.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)

async def create_or_update_admin() -> None:
    async with async_session_factory() as session:
        user_repository = UserRepository(session)

        auth_service = AuthentikService(settings.authentik_url, settings.users_path, settings.sa_auth_admin_app_api_token)
        user_service = UserService(user_repository, auth_service, None)
        logger.info('Creating admin user')
        try:
            await user_service.check_login_not_occupied_or_raise(settings.admin_login)
        except Exception:
            logger.info(f"Admin user already exists (login={settings.admin_login})")
            return
        user = await user_service.create(
            last_name="Admin",
            first_name="Admin",
            login=settings.admin_login,
            roles=[Role.admin,],
            gender=Gender.male,
            lives_in_dormitory=False
        )
        logger.info(f"Admin user created: {settings.admin_login} id={user.id} pk={user.id}")
        try:
            await user_service.update_password(user.id, settings.admin_password)
            logger.info(f"Admin user password set {settings.admin_login} id={user.id} pk={user.id}")
        except Exception:
            logger.error('Failed to set admin password')
            logger.info('Rolling back authentik admin creation')
            try:
                await auth_service.delete_user(user.pk)
                logger.info('Authentik admin user creation rollback successful')
            except Exception:
                logger.error('Failed to roll back authentik admin creation')
            raise
        await session.commit()


if __name__ == "__main__":
    asyncio.run(create_or_update_admin())
