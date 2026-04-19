from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.models.project import Project


class ApplicationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_project_and_user(self, project_id: int, user_id: int) -> Application | None:
        stmt = select(Application).where(
            Application.project_id == project_id, 
            Application.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_project_by_id(self, project_id: int) -> Project | None:
        stmt = select(Project).where(Project.id == project_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_application(self, project_id: int, user_id: int) -> Application:
        application = Application(
            project_id=project_id, 
            user_id=user_id,
            status="pending",
        )
        self.session.add(application)
        await self.session.commit()
        await self.session.refresh(application)
        return application

    async def get_user_applications(self, user_id: int) -> list[Application]:
        stmt = select(Application).where(Application.user_id == user_id).order_by(Application.id.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_project_ids_with_applications(self, user_id: int) -> set[int]:
        stmt = select(Application.project_id).where(Application.user_id == user_id)
        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    async def get_by_id(self, application_id: int) -> Application | None:
        stmt = select(Application).where(Application.id == application_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, application: Application, status: str):
        application.status = status
        await self.session.commit()
        await self.session.refresh(application)
        return application

    async def get_project_applications(self, project_id: int) -> list[Application]:
        stmt = select(Application).where(Application.project_id == project_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())