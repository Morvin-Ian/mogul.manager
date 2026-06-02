from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select, union_all
from sqlalchemy.ext.asyncio import AsyncSession

import models

from database import get_db
from utils.uuid import is_valid_uuid as _is_valid_uuid
from models.collaboration import MemberRole


class WorkspaceService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def create(self, workspace_data: dict, user_id: int) -> models.Workspace:
        workspace = models.Workspace(**workspace_data, user_id=user_id)
        self.db.add(workspace)
        await self.db.flush()  # get workspace.id without full commit

        owner_member = models.WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user_id,
            role=MemberRole.owner,
            joined_at=datetime.now(UTC),
        )
        self.db.add(owner_member)
        await self.db.commit()
        await self.db.refresh(workspace)
        return workspace

    async def get_by_id(self, workspace_id: int) -> models.Workspace | None:
        result = await self.db.execute(
            select(models.Workspace).where(models.Workspace.id == workspace_id)
        )
        return result.scalars().first()

    async def list_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[models.Workspace]:
        # Return workspaces the user owns OR is a member of via workspace_members
        owned_ids_q = select(models.Workspace.id).where(
            models.Workspace.user_id == user_id
        )
        member_ids_q = select(models.WorkspaceMember.workspace_id).where(
            models.WorkspaceMember.user_id == user_id
        )
        combined = union_all(owned_ids_q, member_ids_q).subquery()
        result = await self.db.execute(
            select(models.Workspace)
            .where(models.Workspace.id.in_(select(combined)))
            .distinct()
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(
        self, workspace: models.Workspace, update_data: dict
    ) -> models.Workspace:
        for key, value in update_data.items():
            if value is not None:
                setattr(workspace, key, value)
        await self.db.commit()
        await self.db.refresh(workspace)
        return workspace

    async def delete(self, workspace: models.Workspace) -> None:
        await self.db.delete(workspace)
        await self.db.commit()

    async def get_by_uuid(self, uuid: str) -> models.Workspace | None:
        if not _is_valid_uuid(uuid):
            return None
        result = await self.db.execute(
            select(models.Workspace).where(models.Workspace.uuid == uuid)
        )
        return result.scalars().first()
