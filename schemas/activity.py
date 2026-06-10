from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    workspace_id: int | None = None
    project_id: int | None = None
    task_id: int | None = None
    user_id: int
    entity_type: str
    entity_id: int
    action: str
    summary: str | None = None
    changes: dict | None = None
    created_at: datetime
    user: "ActivityUser | None" = None


class ActivityUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    profile_path: str | None = None
