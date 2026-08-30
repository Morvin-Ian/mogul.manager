"""The AI vendors this app can talk to.

All three speak the OpenAI chat-completions protocol, so one client shape
serves them all — what differs is the endpoint and whether the vendor has a
default model worth assuming.

DeepSeek publishes its own models, so it has a default. Straitly and BAI are
gateways: they front hundreds of models from every vendor and take on more
every week, so there is no sensible default and `model` is required. They
also differ in how they name a model — Straitly prefixes the vendor
(`anthropic/claude-opus-5`), BAI does not (`gpt-5.2`) — which is why the
placeholder is per-provider rather than one shared example.
"""

from dataclasses import dataclass

from config import settings


class ProviderConfigError(Exception):
    """The provider or model is not usable. The message is safe to show."""


@dataclass(frozen=True)
class ProviderSpec:
    slug: str
    label: str
    description: str
    base_url: str
    default_model: str
    model_example: str
    signup_url: str
    catalog_url: str

    @property
    def is_gateway(self) -> bool:
        """A gateway fronts many vendors, so it cannot guess a model."""
        return not self.default_model


PROVIDERS: dict[str, ProviderSpec] = {
    "deepseek": ProviderSpec(
        slug="deepseek",
        label="DeepSeek",
        description="DeepSeek's own models — cheap, fast, and fine for most work.",
        base_url="https://api.deepseek.com",
        default_model="deepseek-chat",
        model_example="deepseek-chat",
        signup_url="https://platform.deepseek.com/",
        catalog_url="https://api-docs.deepseek.com/quick_start/pricing",
    ),
    "straitly": ProviderSpec(
        slug="straitly",
        label="Straitly",
        description=(
            "A gateway onto many vendors' models. Names them `vendor/model`, "
            "so a model id is required."
        ),
        base_url="https://api.straitly.ai/v1",
        default_model="",
        model_example="anthropic/claude-opus-5",
        signup_url="https://straitly.ai/",
        catalog_url="https://straitly.ai/models",
    ),
    "bai": ProviderSpec(
        slug="bai",
        label="BAI",
        description=(
            "A gateway onto many vendors' models. Names them plainly — "
            "`gpt-5.2`, not `openai/gpt-5.2` — and a model id is required."
        ),
        base_url="https://api.b.ai/v1",
        default_model="",
        model_example="gpt-5.2",
        signup_url="https://chat.b.ai",
        catalog_url="https://docs.b.ai",
    ),
}

DEFAULT_PROVIDER = "deepseek"


def get_spec(slug: str) -> ProviderSpec | None:
    return PROVIDERS.get(slug)


@dataclass(frozen=True)
class ResolvedProvider:
    """Everything needed to open a client — a user's key, or the env's."""

    provider: str
    api_key: str
    base_url: str
    model: str

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.model)


def env_provider() -> ResolvedProvider:
    """The server-wide DeepSeek credentials, used when a user has set none."""
    return ResolvedProvider(
        provider=DEFAULT_PROVIDER,
        api_key=settings.deepseek_api_key.get_secret_value(),
        base_url=settings.deepseek_base_url,
        model=settings.deepseek_model,
    )
