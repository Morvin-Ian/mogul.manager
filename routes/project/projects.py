from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from schemas.project.projects import ProjectCreate, ProjectRead, ProjectUpdate
from services.auth import CurrentUser
from services.project.projects import ProjectService

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"],
)


async def _verify_workspace_ownership(
    workspace_id: int, user_id: int, db
) -> models.Workspace:
    result = await db.execute(
        select(models.Workspace).where(models.Workspace.id == workspace_id)
    )
    workspace = result.scalars().first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
        )
    if workspace.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this workspace",
        )
    return workspace


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _verify_workspace_ownership(project.workspace_id, current_user.id, db)
    return await service.create(project.model_dump(exclude_unset=True))


@router.get("", response_model=list[ProjectRead])
async def list_projects(
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    workspace_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    await _verify_workspace_ownership(workspace_id, current_user.id, db)
    return await service.list_by_workspace(workspace_id, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project = await service.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    await _verify_workspace_ownership(project.workspace_id, current_user.id, db)
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project = await service.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    await _verify_workspace_ownership(project.workspace_id, current_user.id, db)
    return await service.update(project, project_update.model_dump(exclude_unset=True))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project = await service.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    await _verify_workspace_ownership(project.workspace_id, current_user.id, db)
    await service.delete(project)
