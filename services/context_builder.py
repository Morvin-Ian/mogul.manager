from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from services.memory import MemoryService
from services.projects import ProjectService
from services.workspaces import WorkspaceService

# Active task statuses worth surfacing to the agent
_ACTIVE_STATUSES = {
    models.TaskStatus.IN_PROGRESS,
    models.TaskStatus.BLOCKED,
    models.TaskStatus.REVIEW,
}


async def build_context(user_id: int, db: AsyncSession) -> str:
    lines: list[str] = []

    # ── User identity ────────────────────────────────────────────
    lines.append(
        f"Current user ID: {user_id} "
        "(use this as user_id when calling workspace tools)"
    )

    # ── Workspaces + projects snapshot ───────────────────────────
    ws_svc = WorkspaceService(db)  # type: ignore[arg-type]
    proj_svc = ProjectService(db)  # type: ignore[arg-type]

    workspaces = await ws_svc.list_by_user(user_id)
    if workspaces:
        lines.append("\nUser's workspaces and projects:")
        for ws in workspaces:
            if ws.is_archived:
                continue
            lines.append(f"  Workspace: {ws.title!r} (id={ws.id})")
            projects = await proj_svc.list_by_workspace(ws.id)
            for proj in projects:
                if proj.is_archived:
                    continue
                lines.append(
                    f"    Project: {proj.title!r} "
                    f"(id={proj.id}, status={proj.status.value})"
                )
    else:
        lines.append("\nThe user has no workspaces yet.")

    # ── Active task summary (in_progress / blocked / review) ─────
    active_tasks = await _fetch_active_tasks(user_id, db)
    if active_tasks:
        lines.append("\nTasks currently in progress or needing attention:")
        for task in active_tasks[:12]:
            due = f", due {task.due_date.date()}" if task.due_date else ""
            lines.append(
                f"  [{task.status.value}] {task.title!r} "
                f"(project_id={task.project_id}{due})"
            )

    # ── Long-term memories ────────────────────────────────────────
    mem_svc = MemoryService(db)  # type: ignore[arg-type]
    memories = await mem_svc.list_by_user(user_id, limit=15)
    if memories:
        lines.append("\nWhat I know about this user:")
        for mem in memories:
            lines.append(f"  [{mem.memory_type}] {mem.content}")

    return "\n".join(lines)


async def _fetch_active_tasks(
    user_id: int, db: AsyncSession
) -> list[models.Task]:
    result = await db.execute(
        select(models.Task)
        .join(models.Project, models.Task.project_id == models.Project.id)
        .join(models.Workspace, models.Project.workspace_id == models.Workspace.id)
        .where(
            models.Workspace.user_id == user_id,
            models.Task.status.in_(_ACTIVE_STATUSES),
        )
        .order_by(models.Task.due_date.asc().nulls_last())
        .limit(20)
    )
    return list(result.scalars().all())
