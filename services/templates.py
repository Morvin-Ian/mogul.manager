from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db


class TemplateService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def create_from_project(
        self, user_id: int, workspace_id: int, project_id: int, name: str, description: str | None = None
    ) -> models.ProjectTemplate:
        # Load the project with all its tasks and tags
        result = await self.db.execute(
            select(models.Project)
            .where(models.Project.id == project_id)
            .options(
                selectinload(models.Project.tags),
                selectinload(models.Project.tasks).selectinload(models.Task.tags),
            )
        )
        project = result.unique().scalars().first()
        if not project:
            raise ValueError("Project not found")

        template_data = {
            "description": project.description,
            "tags": [{"name": t.name, "color": t.color} for t in project.tags],
            "tasks": [
                {
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority.value if hasattr(t.priority, "value") else t.priority,
                    "tags": [{"name": tag.name, "color": tag.color} for tag in t.tags],
                }
                for t in project.tasks
            ],
        }

        tmpl = models.ProjectTemplate(
            workspace_id=workspace_id,
            user_id=user_id,
            name=name,
            description=description,
            template_data=template_data,
        )
        self.db.add(tmpl)
        await self.db.commit()
        await self.db.refresh(tmpl)
        return tmpl

    async def create_project_from_template(
        self, template_id: int, user_id: int, workspace_id: int, project_name: str, project_description: str | None = None
    ) -> models.Project:
        result = await self.db.execute(
            select(models.ProjectTemplate).where(models.ProjectTemplate.id == template_id)
        )
        tmpl = result.scalars().first()
        if not tmpl:
            raise ValueError("Template not found")

        data = tmpl.template_data

        project = models.Project(
            workspace_id=workspace_id,
            created_by_id=user_id,
            title=project_name,
            description=project_description or data.get("description"),
        )
        self.db.add(project)
        await self.db.flush()

        # Create tags
        tag_map = {}
        for tag_data in data.get("tags", []):
            tag = models.Tag(project_id=project.id, name=tag_data["name"], color=tag_data.get("color", "#6366f1"))
            self.db.add(tag)
            await self.db.flush()
            tag_map[tag_data["name"]] = tag

        # Create tasks
        for task_data in data.get("tasks", []):
            task = models.Task(
                project_id=project.id,
                title=task_data["title"],
                description=task_data.get("description"),
                priority=task_data.get("priority", 2),
            )
            self.db.add(task)
            await self.db.flush()

            # Attach tags
            for tag_ref in task_data.get("tags", []):
                tag = tag_map.get(tag_ref["name"])
                if tag and tag not in task.tags:
                    task.tags.append(tag)

        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def list_by_workspace(self, workspace_id: int) -> list[models.ProjectTemplate]:
        result = await self.db.execute(
            select(models.ProjectTemplate)
            .where(models.ProjectTemplate.workspace_id == workspace_id)
            .order_by(models.ProjectTemplate.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, template_id: int) -> bool:
        result = await self.db.execute(
            select(models.ProjectTemplate).where(models.ProjectTemplate.id == template_id)
        )
        tmpl = result.scalars().first()
        if not tmpl:
            return False
        await self.db.delete(tmpl)
        await self.db.commit()
        return True
