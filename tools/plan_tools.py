import json

from sqlalchemy.ext.asyncio import AsyncSession

import models
from agents.planner import PlannerAgent
from schemas.plans import PlanStepRead
from services.plans import PlanService

PLAN_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_plan",
            "description": (
                "Decompose a high-level goal into an ordered, prioritised action plan. "
                "Call this whenever a user describes a goal that requires multiple steps. "
                "Returns the full plan with auto-generated steps."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Current user ID"},
                    "title": {"type": "string", "description": "The high-level goal"},
                    "description": {
                        "type": "string",
                        "description": "Optional extra context",
                    },
                    "workspace_id": {
                        "type": "integer",
                        "description": "Workspace to associate tasks with",
                    },
                },
                "required": ["user_id", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_plans",
            "description": "List all plans for the current user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_plan",
            "description": "Get full details of a plan including all its steps.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan_id": {"type": "integer"},
                },
                "required": ["plan_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_step_status",
            "description": (
                "Update a plan step's execution status. "
                "Use 'running' when starting a step, 'completed' when done, "
                "'failed' if it could not be completed, 'skipped' to bypass it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "step_id": {"type": "integer"},
                    "status": {
                        "type": "string",
                        "enum": [
                            "pending",
                            "running",
                            "completed",
                            "failed",
                            "skipped",
                        ],
                    },
                    "agent_notes": {
                        "type": "string",
                        "description": "What was done or why it failed",
                    },
                    "linked_task_id": {
                        "type": "integer",
                        "description": "Task created while executing this step",
                    },
                },
                "required": ["step_id", "status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_plan",
            "description": "Update a plan's title, description, or status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["draft", "active", "completed", "cancelled"],
                    },
                },
                "required": ["plan_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_plan",
            "description": "Permanently delete a plan and all its steps.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan_id": {"type": "integer"},
                },
                "required": ["plan_id"],
            },
        },
    },
]

_PRIORITY_MAP = {"low": "low", "medium": "medium", "high": "high", "urgent": "urgent"}


def _serialize_step(step: models.PlanStep) -> dict:
    return PlanStepRead.model_validate(step).model_dump(mode="json")


def _serialize_plan(plan: models.Plan) -> dict:
    return {
        "id": plan.id,
        "title": plan.title,
        "description": plan.description,
        "status": plan.status.value,
        "workspace_id": plan.workspace_id,
        "steps": [_serialize_step(s) for s in plan.steps],
        "progress": _calc_progress(plan.steps),
        "created_at": plan.created_at.isoformat(),
        "updated_at": plan.updated_at.isoformat(),
    }


def _calc_progress(steps: list[models.PlanStep]) -> int:
    if not steps:
        return 0
    done = sum(1 for s in steps if s.status.value in ("completed", "skipped"))
    return round(done / len(steps) * 100)


async def handle(name: str, args: dict, db: AsyncSession) -> str:
    svc = PlanService(db)  # type: ignore[arg-type]

    # ── create_plan ───────────────────────────────────────────────
    if name == "create_plan":
        user_id: int = args["user_id"]
        title: str = args["title"]
        description: str | None = args.get("description")
        workspace_id: int | None = args.get("workspace_id")

        plan = await svc.create(
            user_id,
            {
                "title": title,
                "description": description,
                "workspace_id": workspace_id,
                "status": models.PlanStatus.ACTIVE,
            },
        )

        # Decompose goal into steps
        planner = PlannerAgent()
        raw_steps = await planner.decompose(f"{title}. {description or ''}".strip())

        # Save steps — first pass (collect IDs by index)
        saved_steps: list[models.PlanStep] = []
        for i, raw in enumerate(raw_steps):
            step = await svc.create_step(
                {
                    "plan_id": plan.id,
                    "title": raw.get("title", f"Step {i + 1}"),
                    "description": raw.get("description"),
                    "priority": _PRIORITY_MAP.get(
                        raw.get("priority", "medium"), "medium"
                    ),
                    "status": models.StepStatus.PENDING,
                    "step_order": i,
                    "dependencies": [],  # resolve in second pass
                }
            )
            saved_steps.append(step)

        # Second pass — resolve depends_on indices → actual step IDs
        for i, raw in enumerate(raw_steps):
            dep_indices: list[int] = raw.get("depends_on", [])
            dep_ids = [
                saved_steps[j].id for j in dep_indices if 0 <= j < len(saved_steps)
            ]
            if dep_ids:
                saved_steps[i].dependencies = dep_ids
                await db.commit()

        plan = await svc.get_detail(plan.id)
        return json.dumps({"success": True, "plan": _serialize_plan(plan)})  # type: ignore[arg-type]

    # ── list_plans ────────────────────────────────────────────────
    if name == "list_plans":
        plans = await svc.list_by_user(args["user_id"])
        return json.dumps(
            {
                "plans": [
                    {
                        "id": p.id,
                        "title": p.title,
                        "status": p.status.value,
                        "progress": _calc_progress(p.steps),
                        "step_count": len(p.steps),
                    }
                    for p in plans
                ]
            }
        )

    # ── get_plan ──────────────────────────────────────────────────
    if name == "get_plan":
        plan = await svc.get_detail(args["plan_id"])
        if not plan:
            return json.dumps({"error": f"Plan {args['plan_id']} not found"})
        return json.dumps({"plan": _serialize_plan(plan)})

    # ── update_step_status ────────────────────────────────────────
    if name == "update_step_status":
        step = await svc.get_step(args["step_id"])
        if not step:
            return json.dumps({"error": f"Step {args['step_id']} not found"})
        update_data = {"status": args["status"]}
        if args.get("agent_notes"):
            update_data["agent_notes"] = args["agent_notes"]
        if args.get("linked_task_id"):
            update_data["linked_task_id"] = args["linked_task_id"]
        step = await svc.update_step(step, update_data)
        return json.dumps({"success": True, "step": _serialize_step(step)})

    # ── update_plan ───────────────────────────────────────────────
    if name == "update_plan":
        plan_id: int = args.pop("plan_id")
        plan = await svc.get_by_id(plan_id)
        if not plan:
            return json.dumps({"error": f"Plan {plan_id} not found"})
        plan = await svc.update(plan, {k: v for k, v in args.items() if v is not None})
        plan = await svc.get_detail(plan_id)
        return json.dumps({"success": True, "plan": _serialize_plan(plan)})  # type: ignore[arg-type]

    # ── delete_plan ───────────────────────────────────────────────
    if name == "delete_plan":
        plan = await svc.get_by_id(args["plan_id"])
        if not plan:
            return json.dumps({"error": f"Plan {args['plan_id']} not found"})
        await svc.delete(plan)
        return json.dumps({"success": True, "deleted_plan_id": args["plan_id"]})

    return json.dumps({"error": f"Unknown plan tool: {name}"})
