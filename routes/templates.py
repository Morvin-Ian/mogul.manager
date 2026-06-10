from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from schemas.project.projects import ProjectRead
from schemas.templates import (
    CreateFromTemplate,
    ProjectTemplateCreate,
    ProjectTemplateRead,
    ProjectTemplateUpdate,
)
from services.activity import ActivityService
from services.auth import CurrentUser
from services.project.projects import ProjectService
from services.templates import TemplateService
from services.workspace.collaboration import CollaborationService

router = APIRouter(
    prefix="/api/templates",
    tags=["Project Templates"],
)


@router.post("", response_model=ProjectTemplateRead, status_code=status.HTTP_201_CREATED)
async def create_template(
    body: ProjectTemplateCreate,
    current_user: CurrentUser,
    service: Annotated[TemplateService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    activity: Annotated[ActivityService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project = await db.execute(select(models.Project).where(models.Project.id == body.project_id))
    project = project.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await collab.require_access(project.workspace_id, current_user.id, min_role="admin")

    try:
        tmpl = await service.create_from_project(
            user_id=current_user.id,
            workspace_id=project.workspace_id,
            project_id=body.project_id,
            name=body.name,
            description=body.description,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    await activity.log(
        user_id=current_user.id,
        entity_type="template",
        entity_id=tmpl.id,
        action="created",
        workspace_id=project.workspace_id,
        summary=f"created template \"{tmpl.name}\" from project \"{project.title}\"",
    )
    return tmpl


@router.post("/from-template/{template_id}", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project_from_template(
    template_id: int,
    body: CreateFromTemplate,
    current_user: CurrentUser,
    service: Annotated[TemplateService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    proj_service: Annotated[ProjectService, Depends()],
    activity: Annotated[ActivityService, Depends()],
):
    await collab.require_access(body.workspace_id, current_user.id, min_role="admin")

    try:
        project = await service.create_project_from_template(
            template_id=template_id,
            user_id=current_user.id,
            workspace_id=body.workspace_id,
            project_name=body.name,
            project_description=body.description,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    await activity.log(
        user_id=current_user.id,
        entity_type="project",
        entity_id=project.id,
        action="created_from_template",
        workspace_id=body.workspace_id,
        project_id=project.id,
        summary=f"created project \"{project.title}\" from template",
    )
    # Re-read with task counts
    result = await proj_service.get_by_uuid(project.uuid)
    return ProjectRead.model_validate(result or project)


@router.get("", response_model=list[ProjectTemplateRead])
async def list_templates(
    current_user: CurrentUser,
    collab: Annotated[CollaborationService, Depends()],
    service: Annotated[TemplateService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    workspace_id: int | None = None,
):
    if workspace_id is None:
        return []
    await collab.require_access(workspace_id, current_user.id, min_role="member")
    return await service.list_by_workspace(workspace_id)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    current_user: CurrentUser,
    service: Annotated[TemplateService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.ProjectTemplate).where(models.ProjectTemplate.id == template_id)
    )
    tmpl = result.scalars().first()
    if not tmpl:
        return
    await collab.require_access(tmpl.workspace_id, current_user.id, min_role="admin")
    await service.delete(template_id)
