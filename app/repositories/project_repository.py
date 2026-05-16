from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_project(
        self, 
        title: str, 
        description: str,
        max_participants: int,
        owner_id: int
    ) -> Project:
        project = Project(
            title=title, 
            description=description,
            max_participants=max_participants,
            owner_id=owner_id,
            status="draft"
        )

        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)

        return project

    async def get_all_projects(self) -> list[Project]:
        stmt = (
            select(Project)
            .options(
                selectinload(Project.owner),
                selectinload(Project.applications),
            )
            .order_by(Project.id.desc())
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
