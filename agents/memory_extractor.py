import json
import logging

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from services.memory import MemoryService

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a memory extraction system for a project management AI assistant.

Analyze the conversation exchange and extract only information genuinely worth remembering long-term — things that would change how the AI responds to this user in future conversations.

Extract ONLY these types:
- preference: how the user likes to work, communicate, or structure their projects (e.g. "prefers tasks broken into sub-tasks before starting")
- decision: a significant choice the user made that affects future work (e.g. "decided to use Kanban over Scrum for the team")
- goal: a concrete objective, deadline, or target outcome (e.g. "wants to ship v2 by end of Q3 2025")
- fact: a specific project fact not derivable from structured workspace data (e.g. "the client requires weekly status reports every Monday")

Return JSON only — no markdown, no explanation:
{"memories": [{"type": "preference|decision|goal|fact", "content": "one complete, self-contained sentence", "importance": 1|2|3}]}

If nothing worth remembering was said, return: {"memories": []}

Importance scale:
- 1: mildly useful context
- 2: clearly influences future interactions
- 3: critical — would significantly change how the AI behaves

Rules:
- Maximum 3 memories per exchange
- Skip: task status checks, listing requests, small talk, one-off clarifications
- Skip anything already captured in the structured workspace/project/task data
- Each memory must make sense on its own without any conversation context
- Prefer specific over vague: bad — "user likes organization"; good — "user wants due dates set on all tasks at creation time"\
"""


_DEDUP_THRESHOLD = 0.6


def _is_duplicate(content: str, existing: list) -> bool:
    new_words = set(content.lower().split())
    if not new_words:
        return False
    for mem in existing:
        mem_words = set(mem.content.lower().split())
        if not mem_words:
            continue
        jaccard = len(new_words & mem_words) / len(new_words | mem_words)
        if jaccard >= _DEDUP_THRESHOLD:
            return True
    return False


class MemoryExtractor:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key.get_secret_value(),
            base_url=settings.deepseek_base_url,
        )
        self.model = settings.deepseek_model

    async def extract_and_store(
        self,
        user_id: int,
        conversation_id: int,
        user_message: str,
        assistant_message: str,
        db: AsyncSession,
    ) -> None:
        exchange = (
            f"User: {user_message}\n\nAssistant: {assistant_message}"
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": exchange},
                ],
                temperature=0.2,
                max_tokens=256,
            )
            raw = response.choices[0].message.content or "{}"
            # Strip markdown fences if the model wraps anyway
            raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            data = json.loads(raw)
        except Exception as exc:
            logger.warning("Memory extraction failed: %s", exc)
            return

        memories: list[dict] = data.get("memories", [])
        if not memories:
            return

        svc = MemoryService(db)  # type: ignore[arg-type]
        existing = await svc.list_by_user(user_id, limit=100)

        for item in memories[:3]:
            memory_type = item.get("type", "fact")
            content = item.get("content", "").strip()
            importance = int(item.get("importance", 1))

            if not content or memory_type not in ("preference", "decision", "goal", "fact"):
                continue

            if _is_duplicate(content, existing):
                logger.debug("Skipping duplicate memory for user %d: %s", user_id, content)
                continue

            await svc.create(
                user_id=user_id,
                memory_data={
                    "memory_type": memory_type,
                    "content": content,
                    "importance": max(1, min(3, importance)),
                    "source_conversation_id": conversation_id,
                },
            )
            logger.debug("Stored memory [%s] for user %d: %s", memory_type, user_id, content)
