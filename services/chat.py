from typing import Annotated

from fastapi import Depends
from openai.types.chat import ChatCompletionMessageParam
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db


class ChatService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def create_conversation(
        self, user_id: int, title: str | None = None
    ) -> models.Conversation:
        conv = models.Conversation(user_id=user_id, title=title)
        self.db.add(conv)
        await self.db.commit()
        await self.db.refresh(conv)
        return conv

    async def get_conversation(
        self, conversation_id: int, user_id: int
    ) -> models.Conversation | None:
        result = await self.db.execute(
            select(models.Conversation).where(
                models.Conversation.id == conversation_id,
                models.Conversation.user_id == user_id,
            )
        )
        return result.scalars().first()

    async def list_conversations(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[models.Conversation]:
        result = await self.db.execute(
            select(models.Conversation)
            .where(
                models.Conversation.user_id == user_id,
                models.Conversation.is_archived == False,
            )
            .order_by(models.Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_conversation(
        self, conv: models.Conversation, update_data: dict
    ) -> models.Conversation:
        for key, value in update_data.items():
            if value is not None:
                setattr(conv, key, value)
        await self.db.commit()
        await self.db.refresh(conv)
        return conv

    async def delete_conversation(self, conv: models.Conversation) -> None:
        await self.db.delete(conv)
        await self.db.commit()

    async def add_message(
        self, conversation_id: int, role: str, content: str
    ) -> models.Message:
        msg = models.Message(
            conversation_id=conversation_id, role=role, content=content
        )
        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)

        conv = await self.db.get(models.Conversation, conversation_id)
        if conv:
            conv.updated_at = __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            )
            await self.db.commit()

        return msg

    async def get_messages(
        self, conversation_id: int, skip: int = 0, limit: int = 100
    ) -> list[models.Message]:
        result = await self.db.execute(
            select(models.Message)
            .where(models.Message.conversation_id == conversation_id)
            .order_by(models.Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_context(self, conversation_id: int) -> list[ChatCompletionMessageParam]:
        messages = await self.get_messages(conversation_id)
        result: list[ChatCompletionMessageParam] = []
        for m in messages:
            if m.role == "user":
                result.append({"role": "user", "content": m.content})
            elif m.role == "assistant":
                result.append({"role": "assistant", "content": m.content})
            elif m.role == "system":
                result.append({"role": "system", "content": m.content})
        return result
