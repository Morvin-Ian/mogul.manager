import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from schemas.chat import (
    ConversationCreate,
    ConversationDetail,
    ConversationRead,
    ConversationUpdate,
    MessageRead,
    MessageSend,
)
from services.auth import CurrentUser
from services.chat import ChatService

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


def get_deepseek():
    from services.chat import DeepSeekAgent
    return DeepSeekAgent()


@router.post("/conversations", response_model=ConversationRead, status_code=201)
async def create_conversation(
    data: ConversationCreate,
    current_user: CurrentUser,
    service: Annotated[ChatService, Depends()],
):
    title = data.title or "New Conversation"
    return await service.create_conversation(current_user.id, title)


@router.get("/conversations", response_model=list[ConversationRead])
async def list_conversations(
    current_user: CurrentUser,
    service: Annotated[ChatService, Depends()],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    return await service.list_conversations(current_user.id, skip, limit)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: int,
    current_user: CurrentUser,
    service: Annotated[ChatService, Depends()],
):
    conv = await service.get_conversation(conversation_id, current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = await service.get_messages(conversation_id)
    return ConversationDetail(
        id=conv.id,
        user_id=conv.user_id,
        title=conv.title,
        is_archived=conv.is_archived,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[MessageRead.model_validate(m) for m in messages],
    )


@router.patch("/conversations/{conversation_id}", response_model=ConversationRead)
async def update_conversation(
    conversation_id: int,
    update_data: ConversationUpdate,
    current_user: CurrentUser,
    service: Annotated[ChatService, Depends()],
):
    conv = await service.get_conversation(conversation_id, current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return await service.update_conversation(
        conv, update_data.model_dump(exclude_unset=True)
    )


@router.delete(
    "/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_conversation(
    conversation_id: int,
    current_user: CurrentUser,
    service: Annotated[ChatService, Depends()],
):
    conv = await service.get_conversation(conversation_id, current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await service.delete_conversation(conv)


@router.post(
    "/conversations/{conversation_id}/messages",
)
async def send_message(
    conversation_id: int,
    message: MessageSend,
    current_user: CurrentUser,
    service: Annotated[ChatService, Depends()],
):
    conv = await service.get_conversation(conversation_id, current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await service.add_message(conversation_id, "user", message.content)

    if conv.title == "New Conversation":
        title = message.content[:50]
        if len(message.content) > 50:
            title += "..."
        conv.title = title
        await service.db.commit()

    async def generate():
        collected = []
        context = await service.get_context(conversation_id)
        agent = get_deepseek()
        async for token in agent.stream_response(context):
            collected.append(token)
            yield f"data: {json.dumps({'token': token})}\n\n"

        full_response = "".join(collected)
        msg = await service.add_message(conversation_id, "assistant", full_response)
        yield f"data: {json.dumps({'done': True, 'message': {'id': msg.id, 'role': msg.role, 'content': msg.content, 'created_at': msg.created_at.isoformat()}})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
