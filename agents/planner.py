import json
import logging

from openai import AsyncOpenAI

from config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a project planning AI. Break down a goal into a clear, ordered sequence of 3–8 concrete steps that a project management tool can track.

Return JSON ONLY — no markdown, no explanation:
{
  "steps": [
    {
      "title": "Verb-led action title (5–8 words)",
      "description": "What needs to happen and what done looks like (1–3 sentences)",
      "priority": "low|medium|high|urgent",
      "depends_on": [0, 1]
    }
  ]
}

Rules:
- 3–8 steps, ordered from first to last
- depends_on lists zero-based indices of steps that must complete before this one starts
- The first step never has dependencies
- Each step description must include a clear completion condition — what does "done" look like?
- Titles start with an action verb: "Research", "Draft", "Design", "Implement", "Review", "Deploy", "Validate", "Set up"
- Size steps for a single person to complete in hours to a few days — not vague epics, not micro-tasks
- If a step produces output another step depends on, model that with depends_on
- Assign priority based on how blocking the step is and how time-sensitive it is\
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
