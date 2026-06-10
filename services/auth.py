import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Query, Response, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from config import settings
from database import get_db

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire, "token_type": "access"})
    return jwt.encode(
        to_encode, settings.secret_key.get_secret_value(), algorithm=settings.algorithm
    )


def cookie_secure() -> bool:
    """Whether auth cookies should carry the Secure flag.

    Explicit COOKIE_SECURE setting wins; otherwise inferred from whether the
    app is served over HTTPS (frontend_url scheme).
    """
    if settings.cookie_secure is not None:
        return settings.cookie_secure
    return settings.frontend_url.lower().startswith("https")


async def issue_refresh_cookie(
    response: Response, user_id: int, db: AsyncSession
) -> None:
    """Create a refresh token (JWT + server-side record) and set it as a cookie.

    The DB record makes tokens revocable: logout and rotation mark the row,
    so a stolen cookie can be killed server-side.
    """
    jti = uuid.uuid4().hex
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    token = jwt.encode(
        {"sub": str(user_id), "jti": jti, "exp": expires_at, "token_type": "refresh"},
        _get_refresh_key(),
        algorithm=settings.algorithm,
    )
    db.add(models.RefreshToken(jti=jti, user_id=user_id, expires_at=expires_at))
    await db.commit()
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=cookie_secure(),
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 3600,
        path="/",
    )


def verify_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


def _get_refresh_key() -> str:
    return settings.refresh_secret_key.get_secret_value() if settings.refresh_secret_key else settings.secret_key.get_secret_value()


def verify_refresh_token(token: str) -> tuple[str, str] | None:
    """Return (user_id, jti) if the token is a valid refresh JWT, else None."""
    try:
        payload = jwt.decode(
            token,
            _get_refresh_key(),
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )
        if payload.get("token_type") != "refresh":
            return None
        jti = payload.get("jti")
        if not jti:
            return None
        return payload["sub"], jti
    except jwt.PyJWTError:
        return None


# ── Short-lived stream tokens (SSE auth without long-lived tokens in URLs) ──

_STREAM_TOKEN_TTL_SECONDS = 60


def create_stream_token(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(seconds=_STREAM_TOKEN_TTL_SECONDS)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire, "token_type": "stream"},
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )


def verify_stream_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )
        if payload.get("token_type") != "stream":
            return None
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> models.User:
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(models.User).where(models.User.id == user_id_int),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[models.User, Depends(get_current_user)]


async def get_current_user_from_query(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: str = Query(...),
) -> models.User:
    """Auth dependency for SSE, where EventSource can't set headers.

    Only accepts short-lived (60s) single-purpose stream tokens — never the
    main access token, which would otherwise end up in proxy/access logs.
    """
    user_id = verify_stream_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    result = await db.execute(
        select(models.User).where(models.User.id == user_id_int),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
