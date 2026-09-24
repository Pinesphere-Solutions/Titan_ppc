from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    CurrentUser,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_user,
)
from app.integrations.mail.client import send_password_reset_email
from app.modules.auth.schemas import (
    CurrentUserResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    TokenResponse,
)
from app.modules.auth.service import AuthError, authenticate_user, request_password_reset, reset_password

router = APIRouter(prefix="/auth", tags=["auth"])

# Generic response for forgot-password — always the same message whether
# or not the username exists, so this endpoint can't be used to check
# which emails have accounts.
_FORGOT_PASSWORD_MESSAGE = "If an account exists for that email, we've sent a password reset link."


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="none",  # frontend and backend can be on different origins
        # (e.g. two separate tunnel domains for external review)
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/auth/refresh",  # only sent back on the refresh call
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    tokens = await authenticate_user(db, payload.username, payload.password)
    if tokens is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token, refresh_token = tokens
    _set_auth_cookies(response, access_token, refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, response: Response) -> TokenResponse:
    refresh_token_cookie = request.cookies.get("refresh_token")
    if refresh_token_cookie is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    username, role = decode_refresh_token(refresh_token_cookie)

    new_access_token = create_access_token(username, role)
    new_refresh_token = create_refresh_token(username, role)  # rotated
    _set_auth_cookies(response, new_access_token, new_refresh_token)

    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/auth/refresh")
    return {"status": "logged_out"}


@router.get("/me", response_model=CurrentUserResponse)
async def me(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUserResponse:
    return CurrentUserResponse(username=current_user.username, role=current_user.role)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ForgotPasswordResponse:
    result = await request_password_reset(db, payload.username)
    if result is not None:
        user, raw_token = result
        await db.commit()

        reset_link = f"{settings.frontend_base_url}/reset-password?token={raw_token}"
        # Fire-and-forget, same pattern as the vendor deviation email —
        # don't make the user wait on SMTP.
        background_tasks.add_task(send_password_reset_email, to_address=user.username, reset_link=reset_link)
    else:
        await db.rollback()

    return ForgotPasswordResponse(message=_FORGOT_PASSWORD_MESSAGE)


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password_route(
    payload: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResetPasswordResponse:
    try:
        await reset_password(db, payload.token, payload.new_password)
        await db.commit()
    except AuthError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return ResetPasswordResponse(message="Your password has been reset. You can now sign in.")
