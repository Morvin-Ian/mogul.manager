import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from models.collaboration import WorkspaceMember
from models.documents import DocumentStatus
from services.documents import DocumentService
from services.memory import MemoryService
from services.project.projects import ProjectService
from services.documents.rag import RAGService
from services.workspace.workspaces import WorkspaceService

_ACTIVE_STATUSES = {
    models.TaskStatus.IN_PROGRESS,
    models.TaskStatus.BLOCKED,
    models.TaskStatus.REVIEW,
}

_TASK_DISPLAY_LIMIT = 12
_DOC_DISPLAY_LIMIT = 10
_MEMORY_LIMIT = 15


async def build_context(user_id: int, db: AsyncSession, query: str | None = None) -> str:
    lines: list[str] = []

    lines.append(
        f"Current user ID: {user_id} "
        "(use this as user_id when calling workspace tools)"
    )

    ws_svc   = WorkspaceService(db)   # type: ignore[arg-type]
    proj_svc = ProjectService(db)     # type: ignore[arg-type]
    mem_svc  = MemoryService(db)      # type: ignore[arg-type]
    doc_svc  = DocumentService(db)    # type: ignore[arg-type]

    workspaces, active_tasks, memories, documents = await asyncio.gather(
        ws_svc.list_by_user(user_id),
        _fetch_active_tasks(user_id, db),
        mem_svc.list_by_user(user_id, limit=_MEMORY_LIMIT),
        doc_svc.list_documents(user_id),
    )

    active_workspaces = [ws for ws in workspaces if not ws.is_archived]

    # ── Build lookup maps ──────────────────────────────────────────
    workspace_map: dict[int, models.Workspace] = {}
    project_map:   dict[int, models.Project]   = {}
    project_lists_result: list[list[models.Project]] = []

    if active_workspaces:
        project_lists_result = await asyncio.gather(
            *[proj_svc.list_by_workspace(ws.id) for ws in active_workspaces]
        )
        for ws, projects in zip(active_workspaces, project_lists_result):
            workspace_map[ws.id] = ws
            for proj in projects:
                project_map[proj.id] = proj

    # ── Fetch membership data for all active workspaces ──────────
    ws_ids = [ws.id for ws in active_workspaces]
    my_roles: dict[int, str] = {}          # workspace_id → role
    ws_members: dict[int, list[dict]] = {} # workspace_id → [{username, role}]

    if ws_ids:
        rows = await db.execute(
            select(WorkspaceMember, models.User)
            .join(models.User, WorkspaceMember.user_id == models.User.id)
            .where(WorkspaceMember.workspace_id.in_(ws_ids))
            .order_by(WorkspaceMember.workspace_id, WorkspaceMember.joined_at)
        )
        for member, user in rows.all():
            ws_members.setdefault(member.workspace_id, []).append(
                {"username": user.username, "email": user.email or "", "role": member.role.value}
            )
            if member.user_id == user_id:
                my_roles[member.workspace_id] = member.role.value

    # ── Workspace + Project tree ──────────────────────────────────
    if active_workspaces:
        lines.append("\nWorkspaces and projects:")
        for ws, projects in zip(active_workspaces, project_lists_result):
            active_projects = [p for p in projects if not p.is_archived]
            my_role = my_roles.get(ws.id, "member")
            lines.append(f"\n  Workspace: {ws.title!r} (workspace_id: {ws.id}, your role: {my_role})")
            if ws.description:
                lines.append(f"    Description: {ws.description}")

            members = ws_members.get(ws.id, [])
            if members:
                member_parts = ", ".join(
                    f"{m['username']} <{m['email']}> ({m['role']})" for m in members
                )
                lines.append(f"    Team: {member_parts}")
                lines.append(f"    (Use the email addresses above when assigning tasks)")

            for proj in active_projects:
                lines.append(f"    Project: {proj.title!r} (project_id: {proj.id}, status: {proj.status.value})")
                if proj.description:
                    lines.append(f"      Description: {proj.description}")
                if proj.ai_summary:
                    lines.append(f"      AI summary: {proj.ai_summary}")
    else:
        lines.append("\nThe user has no workspaces yet.")

    # ── Active tasks ──────────────────────────────────────────────
    if active_tasks:
        lines.append("\nTasks currently in progress or needing attention:")
        for task in active_tasks[:_TASK_DISPLAY_LIMIT]:
            proj     = project_map.get(task.project_id)
            ws       = workspace_map.get(proj.workspace_id) if proj else None
            proj_name = proj.title if proj else "unknown project"
            ws_name   = f" [{ws.title}]" if ws else ""
            due       = f", due {task.due_date.date()}" if task.due_date else ""
            assignee  = f", assigned to: {task.assignee_name}" if task.assignee_name else ""
            lines.append(
                f"  [{task.status.value}] {task.title!r} "
                f"— {proj_name}{ws_name}{due}{assignee}"
            )
        if len(active_tasks) > _TASK_DISPLAY_LIMIT:
            lines.append(f"  (showing {_TASK_DISPLAY_LIMIT} of {len(active_tasks)} active tasks)")

    # ── Memories ──────────────────────────────────────────────────
    if memories:
        lines.append("\nWhat I know about this user:")
        for mem in memories:
            lines.append(f"  [{mem.memory_type}] {mem.content}")

    # ── Documents ─────────────────────────────────────────────────
    ready_docs = [d for d in documents if d.status == DocumentStatus.ready]
    if ready_docs:
        lines.append(
            "\nUploaded documents in the AI knowledge base "
            "(use search_documents to query their content):"
        )
        for doc in ready_docs[:_DOC_DISPLAY_LIMIT]:
            proj = project_map.get(doc.project_id) if doc.project_id else None
            ws   = workspace_map.get(proj.workspace_id) if proj else None
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
            lines.append(f"  (showing {_DOC_DISPLAY_LIMIT} of {len(ready_docs)} ready documents)")

    # ── RAG context (semantic search over documents) ──────────────
    if query and ready_docs:
        try:
            rag_svc = RAGService(db)  # type: ignore[arg-type]
            rag_context = await rag_svc.build_rag_context(query, user_id)
            if rag_context:
                lines.append(f"\n{rag_context}")
        except Exception:
            pass

    return "\n".join(lines)


async def _fetch_active_tasks(user_id: int, db: AsyncSession) -> list[models.Task]:
    """
    Fetch in-progress / blocked / review tasks from ALL workspaces the user
    is a member of (not just workspaces they own).
    """
    accessible_ws_ids = (
        select(WorkspaceMember.workspace_id)
        .where(WorkspaceMember.user_id == user_id)
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
