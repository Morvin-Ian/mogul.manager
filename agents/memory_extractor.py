import json
import logging

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from utils.prompts import MEMORY_EXTRACTION_SYSTEM
from services.memory import MemoryService

logger = logging.getLogger(__name__)

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
                    {"role": "system", "content": MEMORY_EXTRACTION_SYSTEM},
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
