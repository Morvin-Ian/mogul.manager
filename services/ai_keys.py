"""A user's own AI provider credentials.

The agent used to read one set of DeepSeek credentials out of the
environment. It now asks this service, which prefers whatever key the user
stored and falls back to the environment when they have stored none — so an
existing deployment keeps working untouched.
"""

import logging

from openai import APIError, AsyncOpenAI
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

import models
from agents.providers import (
    PROVIDERS,
    ProviderConfigError,
    ProviderSpec,
    ResolvedProvider,
    env_provider,
    get_spec,
)
from utils.crypto import decrypt_secret, encrypt_secret, key_hint

logger = logging.getLogger(__name__)

VALIDATE_TIMEOUT = 15.0


def resolve_model(spec: ProviderSpec, model: str | None) -> str:
    """The model to call, falling back to the provider's default.

    A gateway has no default — it fronts hundreds of models — so an unset
    model there is an error rather than something to guess at.
    """
    chosen = (model or "").strip() or spec.default_model
    if not chosen:
        raise ProviderConfigError(
            f"{spec.label} needs a model id (for example {spec.model_example})."
        )
    return chosen


class AIKeyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_keys(self, user_id: int) -> list[models.UserAIKey]:
        result = await self.db.execute(
            select(models.UserAIKey).where(models.UserAIKey.user_id == user_id)
        )
        return list(result.scalars())

    async def get_key(self, user_id: int, provider: str) -> models.UserAIKey | None:
        result = await self.db.execute(
            select(models.UserAIKey).where(
                models.UserAIKey.user_id == user_id,
                models.UserAIKey.provider == provider,
            )
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        user_id: int,
        provider: str,
        api_key: str | None,
        model: str | None,
        activate: bool = True,
    ) -> models.UserAIKey:
        """Store or update one provider's credentials for a user.

        `api_key` may be omitted when a key is already stored, so the model
        can be changed without the user pasting the key again.
        """
        spec = get_spec(provider)
        if spec is None:
            raise ProviderConfigError(f"Unknown provider {provider!r}.")

        record = await self.get_key(user_id, provider)
        api_key = (api_key or "").strip()
        if not api_key and record is None:
            raise ProviderConfigError(f"An API key is required for {spec.label}.")

        model = (model or "").strip() or None
        # Surfaces "this gateway needs a model" before anything is written.
        resolve_model(spec, model)

        if record is None:
            record = models.UserAIKey(user_id=user_id, provider=provider)
            self.db.add(record)

        if api_key:
            record.api_key_encrypted = encrypt_secret(api_key)
            record.key_hint = key_hint(api_key)
        record.model = model

        if activate:
            await self._deactivate_others(user_id, provider)
            record.is_active = True

        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def activate(self, user_id: int, provider: str) -> models.UserAIKey:
        record = await self.get_key(user_id, provider)
        if record is None:
            raise ProviderConfigError(f"No {provider} key stored.")
        await self._deactivate_others(user_id, provider)
        record.is_active = True
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def delete(self, user_id: int, provider: str) -> bool:
        record = await self.get_key(user_id, provider)
        if record is None:
            return False
        await self.db.delete(record)
        await self.db.commit()
        return True

    async def _deactivate_others(self, user_id: int, provider: str) -> None:
        await self.db.execute(
            update(models.UserAIKey)
            .where(
                models.UserAIKey.user_id == user_id,
                models.UserAIKey.provider != provider,
            )
            .values(is_active=False)
        )


async def resolve_for_user(user_id: int, db: AsyncSession) -> ResolvedProvider:
    """The credentials the agent should use for this user.

    Their active key if they have one, otherwise the server's environment
    credentials. A stored key that will not decrypt (the encryption secret
    was rotated) is treated as absent rather than fatal.
    """
    result = await db.execute(
        select(models.UserAIKey).where(
            models.UserAIKey.user_id == user_id,
            models.UserAIKey.is_active.is_(True),
        )
    )
    record = result.scalars().first()
    if record is None:
        return env_provider()

    spec = get_spec(record.provider)
    if spec is None:
        logger.warning("User %s has a key for unknown provider %s", user_id, record.provider)
        return env_provider()

    api_key = decrypt_secret(record.api_key_encrypted)
    if not api_key:
        return env_provider()

    try:
        model = resolve_model(spec, record.model)
    except ProviderConfigError as exc:
        logger.warning("User %s provider %s unusable: %s", user_id, spec.slug, exc)
        return env_provider()

    return ResolvedProvider(
        provider=spec.slug, api_key=api_key, base_url=spec.base_url, model=model
    )


async def validate_credentials(
    provider: str, api_key: str, model: str | None
) -> tuple[bool, str]:
    """Ask the provider whether the key works. Returns (ok, message).

    A one-token completion rather than a model listing: it proves the key can
    actually run the model that was chosen, which is what the user cares
    about, and every one of these providers speaks it.
    """
    spec = get_spec(provider)
    if spec is None:
        return False, f"Unknown provider {provider!r}."
    try:
        chosen = resolve_model(spec, model)
    except ProviderConfigError as exc:
        return False, str(exc)

    client = AsyncOpenAI(
        api_key=api_key, base_url=spec.base_url, timeout=VALIDATE_TIMEOUT
    )
    try:
        await client.chat.completions.create(
            model=chosen,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
        )
        return True, f"Connected to {spec.label} using {chosen}."
    except APIError as exc:
        return False, getattr(exc, "message", None) or str(exc)
    except (OSError, ValueError) as exc:
        return False, f"Could not reach {spec.label}: {exc}"
    finally:
        await client.close()


def provider_catalog() -> list[ProviderSpec]:
    return list(PROVIDERS.values())
