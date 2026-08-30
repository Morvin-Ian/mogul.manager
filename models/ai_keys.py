from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import TimestampedModel

if TYPE_CHECKING:
    from .users import User


class UserAIKey(TimestampedModel):
    """One user's credentials for one AI provider.

    A user may store a key per provider and switch between them; `is_active`
    marks the one the agent actually uses, and the service keeps at most one
    active per user.
    """

    __tablename__ = "user_ai_keys"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_user_ai_keys_user_provider"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    # Fernet ciphertext — see utils.crypto. Never leaves the server.
    api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    # Last four characters, so the UI can show which key is stored.
    key_hint: Mapped[str] = mapped_column(String(8), nullable=False, default="")
    # None means "the provider's default"; required for the gateways, which
    # have no default to fall back on.
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user: Mapped["User"] = relationship(back_populates="ai_keys")
