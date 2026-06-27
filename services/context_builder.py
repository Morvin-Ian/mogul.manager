import asyncio
from datetime import datetime, timezone

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from config import settings
from models.collaboration import WorkspaceMember
from models.documents import DocumentStatus
from services.documents import DocumentService
from services.documents.rag import RAGService
from services.memory import MemoryService
from services.project.projects import ProjectService
from services.workspace.workspaces import WorkspaceService

_ACTIVE_STATUSES = {
    models.TaskStatus.IN_PROGRESS,
    models.TaskStatus.BLOCKED,
    models.TaskStatus.REVIEW,
}

_TASK_DISPLAY_LIMIT = settings.task_display_limit
_DOC_DISPLAY_LIMIT = settings.doc_display_limit
_MEMORY_LIMIT = settings.memory_limit


async def build_context(
    user_id: int, db: AsyncSession, query: str | None = None
) -> str:
    lines: list[str] = []

    user_result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = user_result.scalars().first()
    if user:
        lines.append(f"Current user: {user.username} ({user.email})")
        lines.append(
            f"Current user ID: {user_id} "
            "(use this as user_id when calling workspace tools)"
        )
    else:
        lines.append(
            f"Current user ID: {user_id} "
            "(use this as user_id when calling workspace tools)"
        )

    ws_svc = WorkspaceService(db)
    proj_svc = ProjectService(db)
    mem_svc = MemoryService(db)
    doc_svc = DocumentService(db)

    workspaces, active_tasks, memories, documents = await asyncio.gather(
        ws_svc.list_by_user(user_id),
        _fetch_active_tasks(user_id, db),
        mem_svc.list_by_user(user_id, limit=_MEMORY_LIMIT),
        doc_svc.list_documents(user_id, limit=_DOC_DISPLAY_LIMIT),
    )

    active_workspaces = [ws for ws in workspaces if not ws.is_archived]

    workspace_map: dict[int, models.Workspace] = {}
    project_map: dict[int, models.Project] = {}
    project_lists_result: list[list[models.Project]] = []

    if active_workspaces:
        project_lists_result = await asyncio.gather(
            *[proj_svc.list_by_workspace(ws.id) for ws in active_workspaces]
        )
        for ws, projects in zip(active_workspaces, project_lists_result):
            workspace_map[ws.id] = ws
            for proj in projects:
                project_map[proj.id] = proj

    ws_ids = [ws.id for ws in active_workspaces]
    my_roles: dict[int, str] = {}
    ws_members: dict[int, list[dict]] = {}

    if ws_ids:
        rows = await db.execute(
            select(WorkspaceMember, models.User)
            .join(models.User, WorkspaceMember.user_id == models.User.id)
            .where(WorkspaceMember.workspace_id.in_(ws_ids))
            .order_by(WorkspaceMember.workspace_id, WorkspaceMember.joined_at)
        )
        for member, user_row in rows.all():
            ws_members.setdefault(member.workspace_id, []).append(
                {
                    "username": user_row.username,
                    "email": user_row.email or "",
                    "role": member.role.value,
                }
            )
            if member.user_id == user_id:
                my_roles[member.workspace_id] = member.role.value

    all_project_ids = [
        p.id
        for ws, projects in zip(active_workspaces, project_lists_result)
        for p in projects
        if not p.is_archived
    ]

    global_task_total = 0
    global_task_counts: dict[str, int] = {}
    global_overdue = 0
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if all_project_ids:
        count_rows = await db.execute(
            select(models.Task.status, func.count().label("cnt"))
            .where(models.Task.project_id.in_(all_project_ids))
            .group_by(models.Task.status)
        )
        for status, cnt in count_rows.all():
            global_task_total += cnt
            global_task_counts[status.value] = cnt

        overdue_result = await db.execute(
            select(func.count())
            .select_from(models.Task)
            .where(
                models.Task.project_id.in_(all_project_ids),
                models.Task.due_date.isnot(None),
                models.Task.due_date < now,
                models.Task.status != models.TaskStatus.COMPLETED,
            )
        )
        global_overdue = overdue_result.scalar() or 0

    lines.append(
        f"\nGlobal overview: {len(active_workspaces)} active workspace(s), "
        f"{len(all_project_ids)} project(s), {global_task_total} total tasks"
    )
    if global_task_counts:
        parts = ", ".join(
            f"{k.replace('_', ' ')}: {v}" for k, v in sorted(global_task_counts.items())
        )
        lines.append(f"  Task breakdown — {parts}")
    if global_overdue:
        lines.append(f"  Overdue tasks: {global_overdue}")

    if active_workspaces:
        lines.append("\nWorkspaces and projects:")
        for ws, projects in zip(active_workspaces, project_lists_result):
            active_projects = [p for p in projects if not p.is_archived]
            my_role = my_roles.get(ws.id, "member")
            lines.append(
                f"\n  Workspace: {ws.title!r} (workspace_id: {ws.id}, your role: {my_role})"
            )
            if ws.description:
                lines.append(f"    Description: {ws.description}")

            members = ws_members.get(ws.id, [])
            if members:
                member_parts = ", ".join(
                    f"{m['username']} ({m['role']})" for m in members
                )
                email_map = "; ".join(f"{m['username']}={m['email']}" for m in members)
                lines.append(f"    Team: {member_parts}")
                lines.append(
                    f"    (Internal — member emails for tool calls: {email_map})"
                )

            proj_task_counts = await _fetch_project_task_summaries(
                [p.id for p in active_projects], db
            )
            proj_deadlines = await _fetch_project_nearest_deadlines(
                [p.id for p in active_projects], db
            )

            for proj in active_projects:
                lines.append(
                    f"    Project: {proj.title!r} (project_id: {proj.id}, status: {proj.status.value})"
                )
                if proj.description:
                    lines.append(f"      Description: {proj.description}")
                if proj.ai_summary:
                    lines.append(f"      AI summary: {proj.ai_summary}")

                counts = proj_task_counts.get(proj.id, {})
                if counts:
                    total = sum(counts.values())
                    done = counts.get("completed", 0)
                    pct = round(done / total * 100) if total else 0
                    parts = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
                    lines.append(f"      Tasks ({total} total, {pct}% done) — {parts}")
                deadline_info = proj_deadlines.get(proj.id)
                if deadline_info:
                    lines.append(f"      Nearest deadline: {deadline_info}")
    else:
        lines.append("\nThe user has no workspaces yet.")

    if active_tasks:
        lines.append("\nTasks currently in progress or needing attention:")
        for task in active_tasks[:_TASK_DISPLAY_LIMIT]:
            proj = project_map.get(task.project_id)
            ws = workspace_map.get(proj.workspace_id) if proj else None
            proj_name = proj.title if proj else "unknown project"
            ws_name = f" [{ws.title}]" if ws else ""
            due = f", due {task.due_date.date()}" if task.due_date else ""
            assignee = (
                f", assigned to: {task.assignee_name}" if task.assignee_name else ""
            )
            overdue = (
                " [OVERDUE]"
                if task.due_date
                and task.due_date < now
                and task.status != models.TaskStatus.COMPLETED
                else ""
            )
            lines.append(
                f"  [{task.status.value}] {task.title!r} "
                f"— {proj_name}{ws_name}{due}{assignee}{overdue}"
            )
        if len(active_tasks) > _TASK_DISPLAY_LIMIT:
            lines.append(
                f"  (showing {_TASK_DISPLAY_LIMIT} of {len(active_tasks)} active tasks)"
            )

    if memories:
        lines.append("\nWhat I know about this user:")
        for mem in memories:
            lines.append(f"  [{mem.memory_type}] {mem.content}")

    ready_docs = [d for d in documents if d.status == DocumentStatus.ready]
    if ready_docs:
        lines.append(
            "\nUploaded documents in the AI knowledge base "
            "(use search_documents to query their content):"
        )
        for doc in ready_docs[:_DOC_DISPLAY_LIMIT]:
            proj = project_map.get(doc.project_id) if doc.project_id else None
            ws = workspace_map.get(proj.workspace_id) if proj else None
            if proj and ws:
                scope = f"Project: {proj.title!r} in Workspace: {ws.title!r}"
            elif proj:
                scope = f"Project: {proj.title!r}"
            else:
                scope = "General — not linked to any project"
            snippet = (doc.summary or "")[:120].replace("\n", " ")
            summary_note = f" — {snippet}" if snippet else ""
            lines.append(
                f"  {doc.title!r} ({doc.file_type.value}, "
                f"{doc.word_count or 0} words) | {scope}{summary_note}"
            )
        if len(ready_docs) > _DOC_DISPLAY_LIMIT:
            lines.append(
                f"  (showing {_DOC_DISPLAY_LIMIT} of {len(ready_docs)} ready documents)"
            )

    if query and ready_docs:
        try:
            rag_svc = RAGService(db)
            rag_context = await rag_svc.build_rag_context(query, user_id)
            if rag_context:
                lines.append(f"\n{rag_context}")
        except (ValueError, RuntimeError, ConnectionError):
            logger = __import__('logging').getLogger(__name__)
            logger.exception("Failed to build RAG context for user %d", user_id)

    return "\n".join(lines)


async def _fetch_project_task_summaries(
    project_ids: list[int], db: AsyncSession
) -> dict[int, dict[str, int]]:
    if not project_ids:
        return {}
    rows = await db.execute(
        select(models.Task.project_id, models.Task.status, func.count().label("cnt"))
        .where(models.Task.project_id.in_(project_ids))
        .group_by(models.Task.project_id, models.Task.status)
    )
    result: dict[int, dict[str, int]] = {}
    for project_id, status, cnt in rows.all():
        result.setdefault(project_id, {})[status.value] = cnt
    return result


async def _fetch_project_nearest_deadlines(
    project_ids: list[int], db: AsyncSession
) -> dict[int, str]:
    if not project_ids:
        return {}
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    overdue_case = case(
        ((models.Task.due_date < now) & (models.Task.status != models.TaskStatus.COMPLETED), 1),
        else_=0,
    )
    rows = await db.execute(
        select(
            models.Task.project_id,
            func.min(models.Task.due_date).label("nearest"),
            func.sum(overdue_case).label("overdue_count"),
        )
        .where(
            models.Task.project_id.in_(project_ids),
            models.Task.due_date.isnot(None),
        )
        .group_by(models.Task.project_id)
    )
    result: dict[int, str] = {}
    for pid, nearest, overdue in rows.all():
        parts = [nearest.date().isoformat()]
        if overdue:
            parts.append(f"{overdue} overdue")
        result[pid] = " | ".join(parts)
    return result


async def _fetch_active_tasks(user_id: int, db: AsyncSession) -> list[models.Task]:
    accessible_ws_ids = select(WorkspaceMember.workspace_id).where(
        WorkspaceMember.user_id == user_id
    )
    result = await db.execute(
        select(models.Task)
        .join(models.Project, models.Task.project_id == models.Project.id)
        .options(selectinload(models.Task.assignee))
        .where(
            models.Project.workspace_id.in_(accessible_ws_ids),
            models.Task.status.in_(_ACTIVE_STATUSES),
        )
        .order_by(models.Task.due_date.asc().nulls_last())
        .limit(20)
    )
    return list(result.unique().scalars().all())
