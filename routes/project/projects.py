from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

import models
from models.collaboration import MemberRole
from schemas.project.projects import ProjectCreate, ProjectRead, ProjectUpdate
from services.auth import CurrentUser
from services.project.projects import ProjectService
from services.workspace.collaboration import CollaborationService

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"],
)


async def _require_workspace_member(
    workspace_id: int,
    current_user: models.User,
    collab: CollaborationService,
    min_role: str = "member",
) -> models.WorkspaceMember:
    member = await collab.require_access(
        workspace_id, current_user.id, min_role=min_role
    )
    return member


async def _get_project_or_404(
    project_id: str, service: ProjectService
) -> models.Project:
    project = await service.get_by_uuid(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
):
    await _require_workspace_member(
        project.workspace_id, current_user, collab, min_role="admin"
    )
    data = project.model_dump(exclude_unset=True)
    data["created_by_id"] = current_user.id
    return await service.create(data)


@router.get("", response_model=list[ProjectRead])
async def list_projects(
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    workspace_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    if workspace_id is None:
        return await service.list_all_accessible(
            current_user.id, skip=skip, limit=limit
        )
    await _require_workspace_member(
        workspace_id, current_user, collab, min_role="member"
    )
    return await service.list_by_workspace(workspace_id, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str,
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
):
    project = await _get_project_or_404(project_id, service)
    await _require_workspace_member(
        project.workspace_id, current_user, collab, min_role="member"
    )
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
):
    project = await _get_project_or_404(project_id, service)
    member = await _require_workspace_member(
        project.workspace_id, current_user, collab, min_role="member"
    )
    # Members can only edit if they created the project; admins/owners can edit any
    if member.role == MemberRole.member and project.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project creator or an admin can edit this project",
        )
    return await service.update(project, project_update.model_dump(exclude_unset=True))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: CurrentUser,
    service: Annotated[ProjectService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
):
    project = await _get_project_or_404(project_id, service)
    await _require_workspace_member(
        project.workspace_id, current_user, collab, min_role="admin"
    )
    await service.delete(project)
