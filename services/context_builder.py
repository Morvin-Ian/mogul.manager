import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from models.documents import DocumentStatus
from services.documents import DocumentService
from services.memory import MemoryService
from services.plans import PlanService
from services.project.projects import ProjectService
from services.documents.rag import RAGService
from services.workspace.workspaces import WorkspaceService

_ACTIVE_STATUSES = {
    models.TaskStatus.IN_PROGRESS,
    models.TaskStatus.BLOCKED,
    models.TaskStatus.REVIEW,
}

_TASK_DISPLAY_LIMIT = 12
_PENDING_STEP_DISPLAY_LIMIT = 3
_DOC_DISPLAY_LIMIT = 10
_MEMORY_LIMIT = 15
_PLAN_DISPLAY_LIMIT = 5


async def build_context(user_id: int, db: AsyncSession, query: str | None = None) -> str:
    lines: list[str] = []

    lines.append(
        f"Current user ID: {user_id} "
        "(use this as user_id when calling workspace tools)"
    )

    ws_svc = WorkspaceService(db)  # type: ignore[arg-type]
    proj_svc = ProjectService(db)  # type: ignore[arg-type]
    plan_svc = PlanService(db)  # type: ignore[arg-type]
    mem_svc = MemoryService(db)  # type: ignore[arg-type]
    doc_svc = DocumentService(db)  # type: ignore[arg-type]

    # Run all independent top-level queries in parallel
    workspaces, active_tasks, plans, memories, documents = await asyncio.gather(
        ws_svc.list_by_user(user_id),
        _fetch_active_tasks(user_id, db),
        plan_svc.list_by_user(user_id),
        mem_svc.list_by_user(user_id, limit=_MEMORY_LIMIT),
        doc_svc.list_documents(user_id),
    )

    # Workspaces — fetch all projects in parallel once workspace IDs are known
    active_workspaces = [ws for ws in workspaces if not ws.is_archived]
    if active_workspaces:
        project_lists = await asyncio.gather(
            *[proj_svc.list_by_workspace(ws.id) for ws in active_workspaces]
        )
        lines.append("\nUser's workspaces and projects:")
        for ws, projects in zip(active_workspaces, project_lists):
            lines.append(f"  Workspace: {ws.title!r} (id={ws.id})")
            for proj in projects:
                if not proj.is_archived:
                    lines.append(
                        f"    Project: {proj.title!r} "
                        f"(id={proj.id}, status={proj.status.value})"
                    )
    else:
        lines.append("\nThe user has no workspaces yet.")

    # Active tasks
    if active_tasks:
        lines.append("\nTasks currently in progress or needing attention:")
        for task in active_tasks[:_TASK_DISPLAY_LIMIT]:
            due = f", due {task.due_date.date()}" if task.due_date else ""
            lines.append(
                f"  [{task.status.value}] {task.title!r} "
                f"(project_id={task.project_id}{due})"
            )
        if len(active_tasks) > _TASK_DISPLAY_LIMIT:
            lines.append(
                f"  (showing {_TASK_DISPLAY_LIMIT} of {len(active_tasks)} active tasks"
                " — use list_tasks to see all)"
            )

    # Active plans
    active_plans = [p for p in plans if p.status.value in ("active", "draft")]
    if active_plans:
        lines.append("\nActive plans:")
        for plan in active_plans[:_PLAN_DISPLAY_LIMIT]:
            total = len(plan.steps)
            done = sum(1 for s in plan.steps if s.status.value in ("completed", "skipped"))
            pending_steps = [s for s in plan.steps if s.status.value == "pending"]
            running_steps = [s for s in plan.steps if s.status.value == "running"]
            lines.append(f"  Plan: {plan.title!r} (id={plan.id}, {done}/{total} steps done)")
            for s in running_steps:
                lines.append(f"    [running] {s.title!r} (step_id={s.id})")
            for s in pending_steps[:_PENDING_STEP_DISPLAY_LIMIT]:
                lines.append(f"    [pending] {s.title!r} (step_id={s.id}, priority={s.priority.value})")
            if len(pending_steps) > _PENDING_STEP_DISPLAY_LIMIT:
                lines.append(
                    f"    ({len(pending_steps) - _PENDING_STEP_DISPLAY_LIMIT} more pending steps"
                    " — use get_plan to see all)"
                )

    # Memories
    if memories:
        lines.append("\nWhat I know about this user:")
        for mem in memories:
            lines.append(f"  [{mem.memory_type}] {mem.content}")

    # Documents
    ready_docs = [d for d in documents if d.status == DocumentStatus.ready]
    if ready_docs:
        lines.append("\nUploaded documents (use search_documents to query them):")
        for doc in ready_docs[:_DOC_DISPLAY_LIMIT]:
            snippet = (doc.summary or "")[:150].replace("\n", " ")
            lines.append(
                f"  [{doc.id}] {doc.title!r} ({doc.file_type.value}, "
                f"{doc.word_count or 0} words) — {snippet}"
            )
        if len(ready_docs) > _DOC_DISPLAY_LIMIT:
            lines.append(
                f"  (showing {_DOC_DISPLAY_LIMIT} of {len(ready_docs)} documents"
                " — use list_documents to see all)"
            )

    # RAG context (best-effort, never blocks chat)
    if query and ready_docs:
        try:
            rag_svc = RAGService(db)  # type: ignore[arg-type]
            rag_context = await rag_svc.build_rag_context(query, user_id)
            if rag_context:
                lines.append(f"\n{rag_context}")
        except Exception:
            pass

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
