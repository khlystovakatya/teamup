from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application
from app.models.project import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_project(
        self, title: str, description: str, max_participants: int, owner_id: int
    ) -> Project:
        project = Project(
            title=title,
            description=description,
            max_participants=max_participants,
            owner_id=owner_id,
            status="draft",
        )

        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)

        return project

    async def get_all_projects(self, search: str | None = None) -> list[Project]:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.owner),
                selectinload(Project.applications),
            )
            .order_by(Project.id.desc())
        )

        if search:
            search_value = f"%{search}%"

            stmt = stmt.where(
                Project.title.ilike(search_value)
                | Project.description.ilike(search_value)
            )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, project_id: int) -> Project | None:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.owner),
                selectinload(Project.applications),
            )
            .where(Project.id == project_id)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, project: Project, status: str) -> Project:
        project.status = status

        await self.session.commit()
        await self.session.refresh(project)

        return project

    async def delete_project(self, project: Project):
        await self.session.execute(
            delete(Application).where(Application.project_id == project.id)
        )

        await self.session.delete(project)
        await self.session.commit()

    async def update_project(
        self,
        project: Project,
        title: str,
        description: str,
        max_participants: int,
    ) -> Project:
        project.title = title
        project.description = description
        project.max_participants = max_participants

        await self.session.commit()
        await self.session.refresh(project)

        return project
