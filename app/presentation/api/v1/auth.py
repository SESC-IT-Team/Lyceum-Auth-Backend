from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.domain.entities.user import User
from app.application.services.auth_service import AuthService
from app.presentation.dependencies import get_auth_service, get_current_user
from app.presentation.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    LogoutRequest,
    VerifyResponse,
)
from app.presentation.dependencies import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    result = await auth_service.login(body.login, body.password)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password",
        )
    return TokenResponse(**result)


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    revoked = await auth_service.logout(body.refresh_token)
    return {"ok": True, "revoked": revoked}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    result = await auth_service.refresh_tokens(body.refresh_token)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
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
