from sqlalchemy import Column, ForeignKey, Table

from models.base import TimestampedModel


task_dependencies = Table(
    "task_dependencies",
    TimestampedModel.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("depends_on_task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
)
