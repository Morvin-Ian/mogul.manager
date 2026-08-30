"""Per-user AI provider settings.

The key never comes back out of this API — the UI shows the provider, the
chosen model and the last four characters, which is enough to tell one
stored key from another.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from agents.providers import get_spec
from database import get_db
from schemas.ai_keys import (
    AIKeyRead,
    AIKeyTest,
    AIKeyTestResult,
    AIKeyUpsert,
    ProviderInfo,
)
from services.ai_keys import (
    AIKeyService,
    ProviderConfigError,
    provider_catalog,
    validate_credentials,
)
from services.auth import CurrentUser
from utils.crypto import decrypt_secret

router = APIRouter(
    prefix="/api/users/me/ai",
    tags=["AI Providers"],
)

DbSession = Annotated[AsyncSession, Depends(get_db)]


def _service(db: DbSession) -> AIKeyService:
    return AIKeyService(db)


Service = Annotated[AIKeyService, Depends(_service)]


def _require_spec(provider: str):
    spec = get_spec(provider)
    if spec is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"Unknown provider '{provider}'."
        )
    return spec


@router.get("/providers", response_model=list[ProviderInfo])
async def list_providers(current_user: CurrentUser, service: Service):
    """Every supported vendor, annotated with what this user has stored."""
    stored = {k.provider: k for k in await service.list_keys(current_user.id)}
    out: list[ProviderInfo] = []
    for spec in provider_catalog():
        record = stored.get(spec.slug)
        out.append(
            ProviderInfo(
                slug=spec.slug,
                label=spec.label,
                description=spec.description,
                base_url=spec.base_url,
                default_model=spec.default_model,
                model_example=spec.model_example,
                signup_url=spec.signup_url,
                catalog_url=spec.catalog_url,
                requires_model=spec.is_gateway,
                configured=record is not None,
                is_active=bool(record and record.is_active),
                key_hint=record.key_hint if record else None,
                model=record.model if record else None,
                updated_at=record.updated_at if record else None,
            )
        )
    return out


@router.put("/providers/{provider}", response_model=AIKeyRead)
async def save_provider(
    provider: str,
    data: AIKeyUpsert,
    current_user: CurrentUser,
    service: Service,
):
    _require_spec(provider)
    try:
        return await service.upsert(
            current_user.id,
            provider,
            api_key=data.api_key,
            model=data.model,
            activate=data.activate,
        )
    except ProviderConfigError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/providers/{provider}/activate", response_model=AIKeyRead)
async def activate_provider(provider: str, current_user: CurrentUser, service: Service):
    _require_spec(provider)
    try:
        return await service.activate(current_user.id, provider)
    except ProviderConfigError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/providers/{provider}/test", response_model=AIKeyTestResult)
async def test_provider(
    provider: str,
    data: AIKeyTest,
    current_user: CurrentUser,
    service: Service,
):
    """Try the credentials against the vendor before committing to them.

    A key in the body is tested as given; without one the stored key is
    tested, so a user can re-check a provider without re-pasting it.
    """
    _require_spec(provider)
    record = await service.get_key(current_user.id, provider)
    api_key = (data.api_key or "").strip()
    model = data.model

    if not api_key:
        if record is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail="No API key to test."
            )
        decrypted = decrypt_secret(record.api_key_encrypted)
        if not decrypted:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="The stored key could not be read. Please enter it again.",
            )
        api_key = decrypted
        if model is None:
            model = record.model

    ok, message = await validate_credentials(provider, api_key, model)
    return AIKeyTestResult(ok=ok, message=message)


@router.delete("/providers/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(provider: str, current_user: CurrentUser, service: Service):
    _require_spec(provider)
    if not await service.delete(current_user.id, provider):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No {provider} key stored."
        )
