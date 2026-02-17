import asyncio

from app.config import settings
from app.domain.enums.gender import Gender
from app.domain.enums.role import Role
from app.infrastructure.database import async_session_factory
from app.infrastructure.repositories.user_repository import UserRepository
from app.application.services.user_service import UserService
from app.application.services.auth_service import AuthService
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository


async def create_admin() -> None:
    async with async_session_factory() as session:
        user_repository = UserRepository(session)
        refresh_token_repository = RefreshTokenRepository(session)
        auth_service = AuthService(user_repository, refresh_token_repository)
        user_service = UserService(user_repository)

        existing_user = await user_service.get_by_login(settings.admin_login)
        if existing_user is not None:
            print(f"Admin user already exists (login={settings.admin_login})")
            return

        password_hash = auth_service.hash_password(settings.admin_password)
        await user_service.create(
            last_name="Admin",
            first_name="Admin",
            login=settings.admin_login,
            password_hash=password_hash,
            role=Role.admin,
            gender=Gender.male,
        )
        await session.commit()
        print(f"Admin user created (login={settings.admin_login}, password=***)")


if __name__ == "__main__":
    asyncio.run(create_admin())
