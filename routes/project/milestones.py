from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from schemas.milestones import MilestoneCreate, MilestoneRead, MilestoneUpdate
from services.activity import ActivityService
from services.auth import CurrentUser
from services.milestones import MilestoneService
from services.workspace.collaboration import CollaborationService

router = APIRouter(
    prefix="/api/projects/{project_id}/milestones",
    tags=["Milestones"],
)


@router.get("", response_model=list[MilestoneRead])
async def list_milestones(
    project_id: int,
    current_user: CurrentUser,
    service: Annotated[MilestoneService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project = await _get_project_or_404(project_id, db)
    await collab.require_access(project.workspace_id, current_user.id, min_role="member")
    return await service.list_by_project(project_id)


@router.post("", response_model=MilestoneRead, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    project_id: int,
    body: MilestoneCreate,
    current_user: CurrentUser,
    service: Annotated[MilestoneService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    activity: Annotated[ActivityService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project = await _get_project_or_404(project_id, db)
    await collab.require_access(project.workspace_id, current_user.id, min_role="admin")
    created = await service.create(project_id, body.name, body.description, body.due_date)
    await activity.log(
        user_id=current_user.id,
        entity_type="milestone",
        entity_id=created.id,
        action="created",
        workspace_id=project.workspace_id,
        project_id=project_id,
        summary=f"created milestone \"{created.name}\"",
    )
    return created


@router.patch("/{milestone_id}", response_model=MilestoneRead)
async def update_milestone(
    project_id: int,
    milestone_id: int,
    body: MilestoneUpdate,
    current_user: CurrentUser,
    service: Annotated[MilestoneService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    activity: Annotated[ActivityService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project = await _get_project_or_404(project_id, db)
    await collab.require_access(project.workspace_id, current_user.id, min_role="member")
    updated = await service.update(
        milestone_id, body.name, body.description,
        body.status.value if body.status else None,
        body.due_date,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Milestone not found")
    changes = body.model_dump(exclude_unset=True)
    if changes:
        await activity.log(
            user_id=current_user.id,
            entity_type="milestone",
            entity_id=updated.id,
            action="updated",
            workspace_id=project.workspace_id,
            project_id=project_id,
            summary=f"updated milestone \"{updated.name}\"",
            changes=changes,
        )
    return updated


@router.delete("/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(
    project_id: int,
    milestone_id: int,
    current_user: CurrentUser,
    service: Annotated[MilestoneService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    activity: Annotated[ActivityService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project = await _get_project_or_404(project_id, db)
    await collab.require_access(project.workspace_id, current_user.id, min_role="admin")

    # Fetch name before deleting for the activity log
    result = await db.execute(
        select(models.Milestone).where(models.Milestone.id == milestone_id)
    )
    m = result.scalars().first()
    if not m:
        return

    ok = await service.delete(milestone_id)
    if not ok:
        return
    await activity.log(
        user_id=current_user.id,
        entity_type="milestone",
        entity_id=milestone_id,
        action="deleted",
        workspace_id=project.workspace_id,
        project_id=project_id,
        summary=f"deleted milestone \"{m.name}\"",
    )


async def _get_project_or_404(project_id: int, db: AsyncSession) -> models.Project:
    result = await db.execute(select(models.Project).where(models.Project.id == project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
