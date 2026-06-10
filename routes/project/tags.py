from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

import models
from database import get_db
from schemas.tags import TagCreate, TagRead, TagUpdate
from services.auth import CurrentUser
from services.tags import TagService
from services.workspace.collaboration import CollaborationService

router = APIRouter(
    prefix="/api",
    tags=["Tags"],
)


@router.get("/projects/{project_id}/tags", response_model=list[TagRead])
async def list_tags(
    project_id: int,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
):
    return await tag_svc.list_by_project(project_id)


@router.post("/projects/{project_id}/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def create_tag(
    project_id: int,
    body: TagCreate,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
):
    return await tag_svc.create(project_id, body.name, body.color)


@router.patch("/projects/{project_id}/tags/{tag_id}", response_model=TagRead)
async def update_tag(
    tag_id: int,
    body: TagUpdate,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
):
    tag = await tag_svc.update(tag_id, body.name, body.color)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.delete("/projects/{project_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
):
    ok = await tag_svc.delete(tag_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tag not found")


@router.post("/tasks/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def attach_tag(
    task_id: int,
    tag_id: int,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
):
    ok = await tag_svc.attach_to_task(task_id, tag_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task or tag not found")


@router.delete("/tasks/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def detach_tag(
    task_id: int,
    tag_id: int,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
):
    ok = await tag_svc.detach_from_task(task_id, tag_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task or tag not found")


@router.get("/tasks/{task_id}/tags", response_model=list[TagRead])
async def list_task_tags(
    task_id: int,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
):
    return await tag_svc.list_task_tags(task_id)
