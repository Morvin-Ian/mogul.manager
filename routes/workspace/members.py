from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

import models
from models.collaboration import InvitationStatus
from schemas.workspace.collaboration import (
    AcceptResponse,
    InvitationInfoResponse,
    InvitationResponse,
    InviteRequest,
    MemberResponse,
    RoleUpdateRequest,
)
from services.auth import CurrentUser
from services.workspace.collaboration import CollaborationService
from utils.email import send_invite_email
from services.workspace.workspaces import WorkspaceService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/workspaces/{workspace_id}/members",
    tags=["Members"],
)


async def _get_workspace_or_404(
    workspace_id: int,
    ws_service: WorkspaceService,
) -> models.Workspace:
    workspace = await ws_service.get_by_id(workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
        )
    return workspace


@router.get("", response_model=list[MemberResponse])
async def list_members(
    workspace_id: int,
    current_user: CurrentUser,
    collab: Annotated[CollaborationService, Depends()],
    ws_service: Annotated[WorkspaceService, Depends()],
):
    await _get_workspace_or_404(workspace_id, ws_service)
    await collab.require_access(workspace_id, current_user.id, min_role="member")
    return await collab.list_members(workspace_id)


@router.post("/invite", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    workspace_id: int,
    body: InviteRequest,
    current_user: CurrentUser,
    collab: Annotated[CollaborationService, Depends()],
    ws_service: Annotated[WorkspaceService, Depends()],
):
    workspace = await _get_workspace_or_404(workspace_id, ws_service)
    await collab.require_access(workspace_id, current_user.id, min_role="admin")

    if body.role not in ("admin", "member"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'admin' or 'member'",
        )

    invitation = await collab.create_invite(
        workspace_id=workspace_id,
        email=body.email,
        role=body.role,
        invited_by_id=current_user.id,
    )

    try:
        await send_invite_email(
            to_email=invitation.email,
            token=invitation.token,
            role=invitation.role.value,
            workspace_title=workspace.title,
            invited_by_username=current_user.username,
        )
    except Exception as exc:
        logger.warning("Invite email failed but invitation was created: %s", exc)

    return InvitationResponse.model_validate(invitation)


@router.get("/invitations", response_model=list[InvitationResponse])
async def list_invitations(
    workspace_id: int,
    current_user: CurrentUser,
    collab: Annotated[CollaborationService, Depends()],
    ws_service: Annotated[WorkspaceService, Depends()],
):
    await _get_workspace_or_404(workspace_id, ws_service)
    await collab.require_access(workspace_id, current_user.id, min_role="admin")
    invitations = await collab.list_invitations(workspace_id)
    return [InvitationResponse.model_validate(inv) for inv in invitations]


@router.delete("/invitations/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_invitation(
    workspace_id: int,
    invitation_id: int,
    current_user: CurrentUser,
    collab: Annotated[CollaborationService, Depends()],
    ws_service: Annotated[WorkspaceService, Depends()],
):
    await _get_workspace_or_404(workspace_id, ws_service)
    await collab.require_access(workspace_id, current_user.id, min_role="admin")

    result = await collab.db.execute(
        select(models.Invitation).where(
            models.Invitation.id == invitation_id,
            models.Invitation.workspace_id == workspace_id,
        )
    )
    invitation = result.scalars().first()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found"
        )

    invitation.status = InvitationStatus.revoked
    await collab.db.commit()


@router.patch("/{user_id}/role", response_model=MemberResponse)
async def update_member_role(
    workspace_id: int,
    user_id: int,
    body: RoleUpdateRequest,
    current_user: CurrentUser,
    collab: Annotated[CollaborationService, Depends()],
    ws_service: Annotated[WorkspaceService, Depends()],
):
    await _get_workspace_or_404(workspace_id, ws_service)
    member = await collab.update_role(
        workspace_id=workspace_id,
        user_id=user_id,
        new_role=body.role,
        by_user_id=current_user.id,
    )
    return MemberResponse.model_validate(member)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    workspace_id: int,
    user_id: int,
    current_user: CurrentUser,
    collab: Annotated[CollaborationService, Depends()],
    ws_service: Annotated[WorkspaceService, Depends()],
):
    await _get_workspace_or_404(workspace_id, ws_service)
    await collab.remove_member(
        workspace_id=workspace_id,
        user_id=user_id,
        by_user_id=current_user.id,
    )


invitations_router = APIRouter(
    prefix="/api/invitations",
    tags=["Invitations"],
)


@invitations_router.get("/{token}", response_model=InvitationInfoResponse)
async def get_invitation_info(
    token: str,
    collab: Annotated[CollaborationService, Depends()],
    ws_service: Annotated[WorkspaceService, Depends()],
):
    result = await collab.db.execute(
        select(models.Invitation).where(models.Invitation.token == token)
    )
    invitation = result.scalars().first()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found"
        )

    workspace = await ws_service.get_by_id(invitation.workspace_id)
    return InvitationInfoResponse(
        id=invitation.id,
        email=invitation.email,
        role=invitation.role.value,
        status=invitation.status.value,
        expires_at=invitation.expires_at,
        workspace={"id": workspace.id if workspace else None, "title": workspace.title if workspace else None},
    )


@invitations_router.post("/{token}/accept", response_model=AcceptResponse, status_code=status.HTTP_200_OK)
async def accept_invitation(
    token: str,
    current_user: CurrentUser,
    collab: Annotated[CollaborationService, Depends()],
):
    member = await collab.accept_invite(token=token, user_id=current_user.id)
    return AcceptResponse.model_validate(member)
