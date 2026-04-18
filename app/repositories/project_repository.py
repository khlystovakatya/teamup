from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_project(
        self, 
        title: str, 
        description: str, 
        owner_id: int
    ) -> Project:
        project = Project(
            title=title, 
            description=description, 
            owner_id=owner_id,
            status="draft"
        )
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def get_all_projects(self) -> list[Project]:
        stmt = select(Project).order_by(Project.id.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
