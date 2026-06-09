from __future__ import annotations

import logging
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import models
from database import get_db
from models.collaboration import InvitationStatus, MemberRole

logger = logging.getLogger(__name__)

ROLE_RANK: dict[MemberRole, int] = {
    MemberRole.owner: 3,
    MemberRole.admin: 2,
    MemberRole.member: 1,
}


class CollaborationService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def member_count(self, workspace_id: int) -> int:
        result = await self.db.execute(
            select(models.WorkspaceMember.id).where(
                models.WorkspaceMember.workspace_id == workspace_id
            )
        )
        return len(result.all())

    async def get_member(
        self, workspace_id: int, user_id: int
    ) -> models.WorkspaceMember | None:
        result = await self.db.execute(
            select(models.WorkspaceMember).where(
                models.WorkspaceMember.workspace_id == workspace_id,
                models.WorkspaceMember.user_id == user_id,
            )
        )
        return result.scalars().first()

    async def require_access(
        self,
        workspace_id: int,
        user_id: int,
        min_role: str = "member",
    ) -> models.WorkspaceMember:
        member = await self.get_member(workspace_id, user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this workspace",
            )
        required_rank = ROLE_RANK[MemberRole(min_role)]
        actual_rank = ROLE_RANK[member.role]
        if actual_rank < required_rank:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires at least {min_role} role",
            )
        return member

    async def list_members(self, workspace_id: int) -> list[dict]:
        result = await self.db.execute(
            select(models.WorkspaceMember, models.User)
            .join(models.User, models.WorkspaceMember.user_id == models.User.id)
            .where(models.WorkspaceMember.workspace_id == workspace_id)
            .order_by(models.WorkspaceMember.joined_at)
        )
        rows = result.all()
        members = []
        for member, user in rows:
            members.append(
                {
                    "id": member.id,
                    "workspace_id": member.workspace_id,
                    "user_id": user.id,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "profile_path": user.profile_path,
                    },
                    "role": member.role.value,
                    "joined_at": member.joined_at,
                    "last_seen_at": member.last_seen_at,
                }
            )
        return members

    async def create_invite(
        self,
        workspace_id: int,
        email: str,
        role: str,
        invited_by_id: int,
    ) -> models.Invitation:
        # Expire any existing pending invitations for the same email + workspace
        existing_result = await self.db.execute(
            select(models.Invitation).where(
                models.Invitation.workspace_id == workspace_id,
                models.Invitation.email == email,
                models.Invitation.status == InvitationStatus.pending,
            )
        )
        for old_inv in existing_result.scalars().all():
            old_inv.status = InvitationStatus.revoked

        token = secrets.token_urlsafe(48)
        invitation = models.Invitation(
            workspace_id=workspace_id,
            email=email,
            role=MemberRole(role),
            token=token,
            invited_by_id=invited_by_id,
            expires_at=datetime.now(UTC) + timedelta(hours=48),
            status=InvitationStatus.pending,
        )
        self.db.add(invitation)
        await self.db.commit()
        await self.db.refresh(invitation)
        return invitation

    async def list_invitations(self, workspace_id: int) -> list[models.Invitation]:
        result = await self.db.execute(
            select(models.Invitation).where(
                models.Invitation.workspace_id == workspace_id,
                models.Invitation.status == InvitationStatus.pending,
            )
        )
        return list(result.scalars().all())

    async def accept_invite(
        self, token: str, user_id: int
    ) -> models.WorkspaceMember:
        result = await self.db.execute(
            select(models.Invitation).where(models.Invitation.token == token)
        )
        invitation = result.scalars().first()

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )
        if invitation.status != InvitationStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invitation is {invitation.status.value}",
            )
        if invitation.expires_at < datetime.now(UTC):
            invitation.status = InvitationStatus.expired
            await self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation has expired",
            )

        # Check not already a member
        existing = await self.get_member(invitation.workspace_id, user_id)
        if existing:
            invitation.status = InvitationStatus.accepted
            invitation.accepted_at = datetime.now(UTC)
            await self.db.commit()
            return existing

        member = models.WorkspaceMember(
            workspace_id=invitation.workspace_id,
            user_id=user_id,
            role=invitation.role,
            joined_at=datetime.now(UTC),
        )
        self.db.add(member)

        invitation.status = InvitationStatus.accepted
        invitation.accepted_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def remove_member(
        self, workspace_id: int, user_id: int, by_user_id: int
    ) -> None:
        target = await self.get_member(workspace_id, user_id)
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )
        if target.role == MemberRole.owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot remove the workspace owner",
            )

        actor = await self.get_member(workspace_id, by_user_id)
        if not actor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this workspace",
            )

        actor_rank = ROLE_RANK[actor.role]
        target_rank = ROLE_RANK[target.role]

        if actor_rank <= target_rank and actor.user_id != by_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to remove this member",
            )
        # Admin can remove member, owner can remove admin or member
        if actor.role == MemberRole.member and actor.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Members can only remove themselves",
            )
        if actor.role == MemberRole.admin and target.role == MemberRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot remove other admins",
            )

        await self.db.delete(target)
        await self.db.commit()

    async def update_role(
        self,
        workspace_id: int,
        user_id: int,
        new_role: str,
        by_user_id: int,
    ) -> models.WorkspaceMember:
        await self.require_access(workspace_id, by_user_id, min_role="owner")

        target = await self.get_member(workspace_id, user_id)
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )
        if target.role == MemberRole.owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change the role of the workspace owner",
            )
        if MemberRole(new_role) == MemberRole.owner:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign owner role via this endpoint",
            )

        target.role = MemberRole(new_role)
        await self.db.commit()
        result = await self.db.execute(
            select(models.WorkspaceMember)
            .options(joinedload(models.WorkspaceMember.user))
            .where(
                models.WorkspaceMember.workspace_id == workspace_id,
                models.WorkspaceMember.user_id == user_id,
            )
        )
        return result.unique().scalars().first()

    async def add_owner(
        self, workspace_id: int, user_id: int
    ) -> models.WorkspaceMember:
        existing = await self.get_member(workspace_id, user_id)
        if existing:
            existing.role = MemberRole.owner
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        member = models.WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=MemberRole.owner,
            joined_at=datetime.now(UTC),
        )
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member
