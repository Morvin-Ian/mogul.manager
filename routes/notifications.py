import asyncio
import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from schemas.notifications import NotificationRead, UnreadCountResponse
from services.auth import CurrentUser, get_current_user_from_query
from services.notifications import (
    NotificationService,
    get_pending_events,
    subscribe_to_sse,
    unsubscribe_from_sse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"],
)


@router.get("", response_model=list[NotificationRead])
async def list_notifications(
    current_user: CurrentUser,
    service: Annotated[NotificationService, Depends()],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return await service.list_by_user(current_user.id, skip=skip, limit=limit)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def unread_count(
    current_user: CurrentUser,
    service: Annotated[NotificationService, Depends()],
):
    count = await service.unread_count(current_user.id)
    return UnreadCountResponse(count=count)


@router.patch("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_as_read(
    notification_id: int,
    current_user: CurrentUser,
    service: Annotated[NotificationService, Depends()],
):
    ok = await service.mark_as_read(notification_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Notification not found")


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_as_read(
    current_user: CurrentUser,
    service: Annotated[NotificationService, Depends()],
):
    await service.mark_all_as_read(current_user.id)


@router.get("/stream")
async def notification_stream(
    current_user: Annotated[models.User, Depends(get_current_user_from_query)],
    service: Annotated[NotificationService, Depends()],
):
    """SSE endpoint for real-time notification delivery."""
    sub_id = subscribe_to_sse(current_user.id)

    async def event_generator():
        try:
            while True:
                events = await get_pending_events(current_user.id)
                for event in events:
                    yield f"data: {event}\n\n"
                await asyncio.sleep(1)
        finally:
            unsubscribe_from_sse(current_user.id, sub_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
