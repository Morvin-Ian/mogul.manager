from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db


class ReportService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def project_report(self, project_id: int) -> dict:
        # Total and completed tasks
        counts = await self.db.execute(
            select(
                func.count(models.Task.id).label("total"),
                func.sum(
                    func.cast(models.Task.status == "completed", func.Integer)
                ).label("completed"),
                func.sum(
                    func.cast(
                        (models.Task.due_date.isnot(None)) & (models.Task.due_date < datetime.now(UTC)) & (models.Task.status != "completed"),
                        func.Integer,
                    )
                ).label("overdue"),
            ).where(models.Task.project_id == project_id)
        )
        row = counts.one()
        total = row.total or 0
        completed = row.completed or 0
        overdue = row.overdue or 0

        # By status
        status_rows = await self.db.execute(
            select(models.Task.status, func.count(models.Task.id))
            .where(models.Task.project_id == project_id)
            .group_by(models.Task.status)
        )
        by_status = [{"status": s, "count": c} for s, c in status_rows.all()]

        # By priority
        priority_rows = await self.db.execute(
            select(models.Task.priority, func.count(models.Task.id))
            .where(models.Task.project_id == project_id)
            .group_by(models.Task.priority)
        )
        by_priority = [{"priority": p, "count": c} for p, c in priority_rows.all()]

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "overdue_tasks": overdue,
            "completion_pct": round((completed / total * 100) if total > 0 else 0, 1),
            "by_status": by_status,
            "by_priority": by_priority,
        }

    async def workspace_report(self, workspace_id: int) -> dict:
        # Count projects
        proj_count = await self.db.execute(
            select(func.count(models.Project.id))
            .where(models.Project.workspace_id == workspace_id, models.Project.is_archived.is_(False))
        )
        total_projects = proj_count.scalar() or 0

        # Aggregate task stats across all projects in the workspace
        counts = await self.db.execute(
            select(
                func.count(models.Task.id).label("total"),
                func.sum(
                    func.cast(models.Task.status == "completed", func.Integer)
                ).label("completed"),
                func.sum(
                    func.cast(
                        (models.Task.due_date.isnot(None)) & (models.Task.due_date < datetime.now(UTC)) & (models.Task.status != "completed"),
                        func.Integer,
                    )
                ).label("overdue"),
            )
            .select_from(models.Task)
            .join(models.Project, models.Task.project_id == models.Project.id)
            .where(
                models.Project.workspace_id == workspace_id,
                models.Project.is_archived.is_(False),
            )
        )
        row = counts.one()
        total = row.total or 0
        completed = row.completed or 0
        overdue = row.overdue or 0

        # By status
        status_rows = await self.db.execute(
            select(models.Task.status, func.count(models.Task.id))
            .select_from(models.Task)
            .join(models.Project, models.Task.project_id == models.Project.id)
            .where(
                models.Project.workspace_id == workspace_id,
                models.Project.is_archived.is_(False),
            )
            .group_by(models.Task.status)
        )
        by_status = [{"status": s, "count": c} for s, c in status_rows.all()]

        from services.workspace.collaboration import CollaborationService
        collab = CollaborationService(self.db)
        member_count = await collab.member_count(workspace_id)

        return {
            "total_projects": total_projects,
            "total_tasks": total,
            "completed_tasks": completed,
            "overdue_tasks": overdue,
            "completion_pct": round((completed / total * 100) if total > 0 else 0, 1),
            "by_status": by_status,
            "member_count": member_count,
        }
