from pydantic import BaseModel


class LoginRequest(BaseModel):
    login: str
    password: str


# Новая схема ответа без refresh_token
class AccessTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str = "bearer"


# Старая TokenResponse больше не нужна, но если используется где-то ещё – можно оставить, но лучше удалить.
# Удаляем RefreshRequest и LogoutRequest, так как они больше не используются.
class VerifyResponse(BaseModel):
    user_id: str
    role: str
    permissions: list[str]