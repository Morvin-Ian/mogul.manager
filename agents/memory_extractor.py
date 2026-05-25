import json
import logging

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from services.memory import MemoryService

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a memory extraction system embedded in a project management AI assistant.

Analyze the conversation exchange provided and extract any information worth remembering about the user long-term.

Only extract HIGH-VALUE information:
- preference: how the user likes to work, tools/styles/formats they prefer
- decision: a significant choice they made about a project or workflow
- goal: something they want to achieve, a deadline, or a target outcome
- fact: an important project-specific fact not derivable from structured data

Return JSON only — no markdown, no explanation:
{"memories": [{"type": "preference|decision|goal|fact", "content": "one concise sentence", "importance": 1|2|3}]}

If nothing important was said, return: {"memories": []}

Rules:
- Maximum 3 memories per exchange
- Importance: 1 = useful to know, 2 = important, 3 = critical
- Skip trivial requests (listing tasks, checking status, small talk)
- Each memory must be a single, self-contained sentence
- Do not duplicate memories that would already be obvious from the workspace data\
"""


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
                max_tokens=512,
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
        for item in memories[:3]:
            memory_type = item.get("type", "fact")
            content = item.get("content", "").strip()
            importance = int(item.get("importance", 1))

            if not content or memory_type not in ("preference", "decision", "goal", "fact"):
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
