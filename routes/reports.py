from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from schemas.reports import ProjectReport, WorkspaceReport
from services.auth import CurrentUser
from services.reports import ReportService
from services.workspace.collaboration import CollaborationService

router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"],
)


@router.get("/project/{project_id}", response_model=ProjectReport)
async def get_project_report(
    project_id: int,
    current_user: CurrentUser,
    report: Annotated[ReportService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Project).where(models.Project.id == project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await collab.require_access(project.workspace_id, current_user.id, min_role="member")
    return await report.project_report(project_id)


@router.get("/workspace/{workspace_id}", response_model=WorkspaceReport)
async def get_workspace_report(
    workspace_id: int,
    current_user: CurrentUser,
    report: Annotated[ReportService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
):
    await collab.require_access(workspace_id, current_user.id, min_role="member")
    return await report.workspace_report(workspace_id)
