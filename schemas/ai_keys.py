from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProviderInfo(BaseModel):
    """One supported vendor, and what this user has stored for it."""

    slug: str
    label: str
    description: str
    base_url: str
    default_model: str
    model_example: str
    signup_url: str
    catalog_url: str
    # A gateway fronts many vendors, so the UI must insist on a model id.
    requires_model: bool

    configured: bool = False
    is_active: bool = False
    # Last four characters of the stored key — never the key itself.
    key_hint: str | None = None
    model: str | None = None
    updated_at: datetime | None = None


class AIKeyUpsert(BaseModel):
    # Optional so the model can be changed without re-pasting the key.
    api_key: str | None = Field(default=None, max_length=400)
    model: str | None = Field(default=None, max_length=120)
    activate: bool = True


class AIKeyTest(BaseModel):
    """Test a key before storing it, or re-test the stored one."""

    api_key: str | None = Field(default=None, max_length=400)
    model: str | None = Field(default=None, max_length=120)


class AIKeyTestResult(BaseModel):
    ok: bool
    message: str


class AIKeyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    provider: str
    key_hint: str
    model: str | None
    is_active: bool
    updated_at: datetime
