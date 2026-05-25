import json
import logging

from openai import AsyncOpenAI

from config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a project planning AI. Decompose the goal into 3 to 8 concrete, actionable steps.

Return JSON ONLY — no markdown, no explanation:
{
  "steps": [
    {
      "title": "Short action title starting with a verb",
      "description": "What exactly needs to be done in 1-2 sentences",
      "priority": "low|medium|high|urgent",
      "depends_on": [0, 1]
    }
  ]
}

Rules:
- 3–8 steps, ordered logically (earliest first)
- depends_on = zero-based indices of steps that MUST finish before this one starts
- First step never has dependencies
- Priority reflects urgency and importance
- Titles start with a verb: "Research...", "Draft...", "Create...", "Review...", "Deploy..."
- Steps should each be independently completable
- If a step produces output used by later steps, express that as a dependency\
"""


class PlannerAgent:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key.get_secret_value(),
            base_url=settings.deepseek_base_url,
        )
        self.model = settings.deepseek_model

    async def decompose(self, goal: str) -> list[dict]:
        """Return a list of step dicts with title, description, priority, depends_on (indices)."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": f"Goal: {goal}"},
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            raw = response.choices[0].message.content or "{}"
            raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            data = json.loads(raw)
            steps = data.get("steps", [])
            if not isinstance(steps, list) or not steps:
                raise ValueError("Empty steps list")
            return steps[:8]
        except Exception as exc:
            logger.warning("Plan decomposition failed: %s", exc)
            # Fallback: single generic step
            return [{"title": goal, "description": None, "priority": "medium", "depends_on": []}]
