# Deliberately light: `agents.chat_agent` pulls in the tool registry, which
# reaches back into services, so importing it here would make any
# `from agents.providers import ...` a circular import. Import the agent
# from its own module instead.
from agents.providers import PROVIDERS, ProviderSpec, ResolvedProvider

__all__ = ["PROVIDERS", "ProviderSpec", "ResolvedProvider"]
