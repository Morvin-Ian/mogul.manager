from __future__ import annotations

import logging
import secrets
import urllib.parse
from datetime import UTC, datetime, timedelta

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from config import settings
from database import get_db
from services.auth import (
    CurrentUser,
    create_access_token,
    create_refresh_token,
    hash_password,
)

logger = logging.getLogger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_SCOPE = "openid email profile"

router = APIRouter(
    prefix="/api/auth",
    tags=["Google OAuth"],
)


def _build_state_token() -> str:
    payload = {
        "purpose": "oauth_state",
        "exp": datetime.now(UTC) + timedelta(minutes=15),
    }
    return jwt.encode(
        payload,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )


def _verify_state_token(state: str) -> bool:
    try:
        payload = jwt.decode(
            state,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
        )
        return payload.get("purpose") == "oauth_state"
    except jwt.PyJWTError:
        return False


def _make_username_from_email(email: str) -> str:
    local = email.split("@")[0]
    # Keep only alphanumeric and underscores, truncate to 40 chars
    cleaned = "".join(c if c.isalnum() or c == "_" else "_" for c in local)[:40]
    return cleaned or "user"


@router.get("/google")
async def google_login() -> RedirectResponse:
    state = _build_state_token()

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_url,
        "response_type": "code",
        "scope": GOOGLE_SCOPE,
        "access_type": "offline",
        "state": state,
        "prompt": "select_account",
    }

    query_string = urllib.parse.urlencode(params)
    redirect_url = f"{GOOGLE_AUTH_URL}?{query_string}"
    return RedirectResponse(url=redirect_url)


@router.get("/google/callback")
async def google_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    error_redirect = f"{settings.frontend_url}/login?error=oauth_failed"

    if error:
        logger.warning("Google OAuth error: %s", error)
        return RedirectResponse(url=error_redirect)

    if not code or not state:
        return RedirectResponse(url=error_redirect)

    if not _verify_state_token(state):
        logger.warning("Invalid OAuth state token")
        return RedirectResponse(url=error_redirect)

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret.get_secret_value(),
                    "redirect_uri": settings.google_redirect_url,
                    "grant_type": "authorization_code",
                },
            )
            token_response.raise_for_status()
            token_data = token_response.json()

            userinfo_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            userinfo_response.raise_for_status()
            userinfo = userinfo_response.json()
    except httpx.HTTPStatusError as exc:
        logger.error("Google token/userinfo request failed: %s", exc)
        return RedirectResponse(url=error_redirect)
    except Exception as exc:
        logger.error("Unexpected error during Google OAuth: %s", exc)
        return RedirectResponse(url=error_redirect)

    google_id: str = userinfo.get("sub", "")
    email: str = userinfo.get("email", "")
    name: str = userinfo.get("name", "")

    if not google_id or not email:
        logger.error("Google userinfo missing sub or email: %s", userinfo)
        return RedirectResponse(url=error_redirect)

    user = await _find_or_create_user(db, google_id=google_id, email=email, name=name)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    response = RedirectResponse(
        url=f"{settings.frontend_url}/auth/callback?token={access_token}"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 3600,
        path="/",
    )
    return response


async def _find_or_create_user(
    db: AsyncSession,
    *,
    google_id: str,
    email: str,
    name: str,
) -> models.User:
    result = await db.execute(
        select(models.User).where(models.User.google_id == google_id)
    )
    user = result.scalars().first()
    if user:
        return user

    # 2. Look up by email (existing non-Google account — link it)
    result = await db.execute(select(models.User).where(models.User.email == email))
    user = result.scalars().first()
    if user:
        user.google_id = google_id
        await db.commit()
        await db.refresh(user)
        return user

    base_username = _make_username_from_email(email)
    username = await _unique_username(db, base_username)

    random_pass = secrets.token_urlsafe(32)
    new_user = models.User(
        username=username,
        email=email,
        password_hash=hash_password(random_pass),
        google_id=google_id,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    logger.info("Created new user via Google OAuth: %s (id=%s)", email, new_user.id)
    return new_user


async def _unique_username(db: AsyncSession, base: str) -> str:
    candidate = base
    suffix = 1
    while True:
        result = await db.execute(
            select(models.User).where(models.User.username == candidate)
        )
        if result.scalars().first() is None:
            return candidate
        candidate = f"{base}{suffix}"
        suffix += 1


@router.post("/google/unlink", status_code=status.HTTP_200_OK)
async def google_unlink(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    if not current_user.google_id:
        raise HTTPException(status_code=400, detail="No Google account is linked.")
    current_user.google_id = None
    await db.commit()
    await db.refresh(current_user)
    return {"message": "Google account unlinked successfully."}
