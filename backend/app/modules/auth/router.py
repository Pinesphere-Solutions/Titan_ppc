from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.auth.schemas import CurrentUserResponse, LoginRequest, TokenResponse
from app.modules.auth.service import authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


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

    # httpOnly, Secure cookie — see architecture doc Section 7.1.
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict",
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie("access_token")
    return {"status": "logged_out"}


@router.get("/me", response_model=CurrentUserResponse)
async def me(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUserResponse:
    return CurrentUserResponse(username=current_user.username, role=current_user.role)
