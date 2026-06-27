from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from utils.email import send_notification_email

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def create(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str | None = None,
        link: str | None = None,
        metadata_json: dict | None = None,
    ) -> models.Notification:
        notif = models.Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            metadata_json=metadata_json,
        )
        self.db.add(notif)
        await self.db.commit()
        await self.db.refresh(notif)
        return notif

    async def list_by_user(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[models.Notification]:
        result = await self.db.execute(
            select(models.Notification)
            .where(models.Notification.user_id == user_id)
            .order_by(models.Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def unread_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(models.Notification.id)
            .where(
                models.Notification.user_id == user_id,
                models.Notification.is_read.is_(False),
            )
        )
        return len(result.all())

    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        result = await self.db.execute(
            update(models.Notification)
            .where(
                models.Notification.id == notification_id,
                models.Notification.user_id == user_id,
            )
            .values(is_read=True, read_at=datetime.now(UTC))
        )
        await self.db.commit()
        return result.rowcount > 0

    async def mark_all_as_read(self, user_id: int) -> int:
        result = await self.db.execute(
            update(models.Notification)
            .where(
                models.Notification.user_id == user_id,
                models.Notification.is_read.is_(False),
            )
            .values(is_read=True, read_at=datetime.now(UTC))
        )
        await self.db.commit()
        return result.rowcount

    async def create_and_notify(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str | None = None,
        link: str | None = None,
        metadata_json: dict | None = None,
        email_to: str | None = None,
        email_subject: str | None = None,
    ) -> models.Notification:
        notif = await self.create(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            metadata_json=metadata_json,
        )
        if email_to and email_subject:
            try:
                await send_notification_email(
                    to_email=email_to,
                    subject=email_subject,
                    title=title,
                    message=message or "",
                    link=link,
                )
            except Exception as exc:
                logger.warning("Failed to send notification email to %s: %s", email_to, exc)
        return notif


# In-memory SSE event bus for real-time notifications
_sse_subscribers: dict[int, list] = {}
_pending_events: dict[int, list[str]] = {}
_last_activity: dict[int, float] = {}  # user_id -> last heartbeat timestamp
_SSE_STALE_TIMEOUT = 120.0  # seconds without heartbeat = stale


def subscribe_to_sse(user_id: int) -> int:
    import random
    from time import monotonic
    sub_id = random.randint(1, 10**9)
    _sse_subscribers.setdefault(user_id, []).append(sub_id)
    _last_activity[user_id] = monotonic()
    return sub_id


def unsubscribe_from_sse(user_id: int, sub_id: int) -> None:
    subs = _sse_subscribers.get(user_id, [])
    if sub_id in subs:
        subs.remove(sub_id)
    if not _sse_subscribers.get(user_id):
        _sse_subscribers.pop(user_id, None)
        _last_activity.pop(user_id, None)


def refresh_sse_activity(user_id: int) -> None:
    from time import monotonic
    _last_activity[user_id] = monotonic()


def cleanup_stale_sse() -> None:
    """Remove subscribers that haven't had activity in _SSE_STALE_TIMEOUT seconds."""
    from time import monotonic
    now = monotonic()
    stale = [uid for uid, last in _last_activity.items() if now - last > _SSE_STALE_TIMEOUT]
    for uid in stale:
        _sse_subscribers.pop(uid, None)
        _pending_events.pop(uid, None)
        _last_activity.pop(uid, None)


async def emit_notification_event(user_id: int, notification: models.Notification) -> None:
    if user_id not in _sse_subscribers or not _sse_subscribers[user_id]:
        return
    payload = json.dumps({
        "type": "notification",
        "uuid": notification.uuid,
        "notification_type": notification.notification_type,
        "title": notification.title,
        "message": notification.message,
        "link": notification.link,
        "created_at": notification.created_at.isoformat(),
    })
    # Store in a request-local way — the SSE generator reads this
    _pending_events.setdefault(user_id, []).append(payload)


async def get_pending_events(user_id: int) -> list[str]:
    return _pending_events.pop(user_id, [])
