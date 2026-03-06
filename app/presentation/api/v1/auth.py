from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer

from app.domain.entities.user import User
from app.application.services.auth_service import AuthService
from app.presentation.dependencies import get_auth_service, get_current_user, limiter
from app.presentation.schemas.auth import (
    LoginRequest,
    TokenResponse,          # возвращаем полный ответ с refresh_token
    VerifyResponse,
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Устанавливает access и refresh токены в http-only cookie."""
    # Access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        path="/",  # можно ограничить, но обычно корень
        max_age=settings.jwt_access_expire_minutes * 60,  # секунды
    )
    # Refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        path="/api/v1/auth/refresh",  # лучше ограничить путь для refresh
        max_age=settings.jwt_refresh_expire_days * 24 * 60 * 60,
    )

def clear_auth_cookies(response: Response):
    """Очищает cookie с токенами."""
    response.delete_cookie("access_token", path="/", domain=settings.cookie_domain)
    response.delete_cookie("refresh_token", path="/api/v1/auth/refresh", domain=settings.cookie_domain)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    result = await auth_service.login(body.login, body.password)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password",
        )
    # Устанавливаем cookie с токенами
    set_auth_cookies(response, result["access_token"], result["refresh_token"])
    # Возвращаем полный ответ (включая refresh_token для удобства тестирования)
    return TokenResponse(**result)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token not found in cookies",
        )
    revoked = await auth_service.logout(refresh_token)
    clear_auth_cookies(response)
    return {"ok": True, "revoked": revoked}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )
    result = await auth_service.refresh_tokens(refresh_token)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    # Обновляем cookie
    set_auth_cookies(response, result["access_token"], result["refresh_token"])
    # Возвращаем полный ответ
    return TokenResponse(**result)


@router.post("/verify", response_model=VerifyResponse)
async def verify(
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    from app.domain.enums.permission import get_permissions_for_role
    perms = [p.value for p in get_permissions_for_role(current_user.role)]
    return VerifyResponse(
        user_id=str(current_user.id),
        role=current_user.role.value,
        permissions=perms,
    )


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    from app.presentation.schemas.user import UserResponse
    return UserResponse(
        id=current_user.id,
        last_name=current_user.last_name,
        first_name=current_user.first_name,
        middle_name=current_user.middle_name,
        role=current_user.role,
        gender=current_user.gender,
        class_name=current_user.class_name,
        graduation_year=current_user.graduation_year,
        login=current_user.login,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )