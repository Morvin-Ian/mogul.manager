from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from schemas.workspace.workspaces import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate
from services.auth import CurrentUser
from services.workspace.collaboration import CollaborationService
from services.workspace.workspaces import WorkspaceService

router = APIRouter(
    prefix="/api/workspaces",
    tags=["Workspaces"],
)


@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace: WorkspaceCreate,
    current_user: CurrentUser,
    service: Annotated[WorkspaceService, Depends()],
):
    return await service.create(
        workspace.model_dump(exclude_unset=True), current_user.id
    )


@router.get("", response_model=list[WorkspaceRead])
async def list_workspaces(
    current_user: CurrentUser,
    service: Annotated[WorkspaceService, Depends()],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    return await service.list_by_user(current_user.id, skip=skip, limit=limit)


@router.get("/{workspace_id}", response_model=WorkspaceRead)
async def get_workspace(
    workspace_id: str,
    current_user: CurrentUser,
    service: Annotated[WorkspaceService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
):
    workspace = await service.get_by_uuid(workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
        )
    await collab.require_access(workspace.id, current_user.id, min_role="member")
    return workspace


@router.patch("/{workspace_id}", response_model=WorkspaceRead)
async def update_workspace(
    workspace_id: str,
    workspace_update: WorkspaceUpdate,
    current_user: CurrentUser,
    service: Annotated[WorkspaceService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
):
    workspace = await service.get_by_uuid(workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
        )
    await collab.require_access(workspace.id, current_user.id, min_role="admin")
    return await service.update(
        workspace, workspace_update.model_dump(exclude_unset=True)
    )


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: str,
    current_user: CurrentUser,
    service: Annotated[WorkspaceService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
):
    workspace = await service.get_by_uuid(workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
        )
    await collab.require_access(workspace.id, current_user.id, min_role="owner")
    await service.delete(workspace)
