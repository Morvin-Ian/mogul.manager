"""Symmetric encryption for secrets we must be able to read back.

Provider API keys are not passwords: the server has to hand the plaintext to
the vendor on every call, so hashing them is not an option. They are
encrypted at rest instead, with a Fernet key derived from a configured
secret.

The derivation means rotating that secret makes every stored key
undecryptable — `decrypt_secret` returns None rather than raising, so a user
is asked to re-enter a key instead of the request failing. Set
`AI_ENCRYPTION_KEY` explicitly to rotate the auth secret independently.
"""

import base64
import hashlib
import logging

from cryptography.fernet import Fernet, InvalidToken

from config import settings

logger = logging.getLogger(__name__)

_fernet_cache: Fernet | None = None


def _fernet() -> Fernet:
    global _fernet_cache
    if _fernet_cache is None:
        secret = (
            settings.ai_encryption_key or settings.secret_key
        ).get_secret_value()
        digest = hashlib.sha256(secret.encode()).digest()
        _fernet_cache = Fernet(base64.urlsafe_b64encode(digest))
    return _fernet_cache


def encrypt_secret(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_secret(token: str) -> str | None:
    """The plaintext, or None if the token was written under another key."""
    try:
        return _fernet().decrypt(token.encode()).decode()
    except (InvalidToken, ValueError) as exc:
        logger.warning("Stored secret could not be decrypted: %s", exc)
        return None


def key_hint(plaintext: str) -> str:
    """The last four characters, for showing which key is stored."""
    return plaintext[-4:] if len(plaintext) >= 4 else "••••"
