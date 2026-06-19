import json

from sqlalchemy.ext.asyncio import AsyncSession

from services.project.plans import PlanService

PLAN_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_plan",
            "description": (
                "Generate an AI-driven plan for a project. "
                "Breaks the goal into ordered steps and automatically creates linked tasks. "
                "Use when the user wants to plan a project, get started, or organise work."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "ID of the project to create the plan for",
                    },
                    "title": {
                        "type": "string",
                        "description": "The goal or objective for the plan (1 sentence)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional additional context or constraints",
                    },
                },
                "required": ["project_id", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_plans",
            "description": "List all plans for a project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer"},
                },
                "required": ["project_id"],
            },
        },
    },
]


async def handle(name: str, args: dict, db: AsyncSession, user_id: int = 0) -> str:
    svc = PlanService(db)

    if name == "create_plan":
        project_id = args.get("project_id")
        title = args.get("title", "").strip()
        description = args.get("description")

        if not project_id or not title:
            return json.dumps({"error": "project_id and title are required"})
        if not user_id:
            return json.dumps({"error": "Cannot create plan: user context missing"})

        try:
            plan = await svc.create(
                project_id=int(project_id),
                user_id=user_id,
                title=title,
                description=description or None,
            )
            return json.dumps(
                {
                    "id": plan.id,
                    "title": plan.title,
                    "status": plan.status.value,
                    "step_count": len(plan.steps),
                    "steps": [
                        {
                            "order": s.step_order + 1,
                            "title": s.title,
                            "priority": s.priority.value,
                            "linked_task": s.linked_task_title,
                        }
                        for s in sorted(plan.steps, key=lambda s: s.step_order)
                    ],
                }
            )
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    if name == "list_plans":
        project_id = args.get("project_id")
        if not project_id:
            return json.dumps({"error": "project_id is required"})
        try:
            plans = await svc.list_by_project(int(project_id))
            return json.dumps(
                [
                    {
                        "id": p.id,
                        "title": p.title,
                        "status": p.status.value,
                        "step_count": len(p.steps),
                        "done_count": sum(
                            1
                            for s in p.steps
                            if s.status.value in ("completed", "skipped")
                        ),
                    }
                    for p in plans
                ]
            )
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    return json.dumps({"error": f"Unknown plan tool: {name}"})
