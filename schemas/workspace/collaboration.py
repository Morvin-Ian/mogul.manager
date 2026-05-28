from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class InviteRequest(BaseModel):
    email: EmailStr
    role: str = "member"


class RoleUpdateRequest(BaseModel):
    role: str


class UserBasic(BaseModel):
    id: int
    username: str | None = None
    email: str | None = None
    profile_path: str | None = None


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workspace_id: int
    user_id: int
    user: UserBasic
    role: str
    joined_at: datetime
    last_seen_at: datetime | None = None


class InvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str
    status: str
    invited_by_id: int | None = None
    expires_at: datetime
    created_at: datetime


class InvitationInfoResponse(BaseModel):
    id: int
    email: str
    role: str
    status: str
    expires_at: datetime
    workspace: dict


class AcceptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workspace_id: int
    user_id: int
    role: str
    joined_at: datetime


class MyMembershipResponse(BaseModel):
    workspace_id: int
    user_id: int
    role: str
    joined_at: datetime
