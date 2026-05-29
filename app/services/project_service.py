from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    async def create_project(self, project_data: ProjectCreate, owner_id: int):
        if project_data.max_participants <= 0:
            raise ValueError("Количество участников должно быть больше 0")

        return await self.project_repository.create_project(
            title=project_data.title,
            description=project_data.description,
            max_participants=project_data.max_participants,
            owner_id=owner_id,
        )

    async def get_all_projects(self):
        return await self.project_repository.get_all_projects()

    def get_accepted_count(self, project: Project) -> int:
        return len(
            [
                application
                for application in project.applications
                if application.status == "accepted"
            ]
        )

    def get_free_slots(self, project: Project) -> int:
        accepted_count = self.get_accepted_count(project)
        return project.max_participants - accepted_count

    async def open_project(self, project_id: int, user_id: int):
        project = await self.project_repository.get_by_id(project_id)

        if not project:
            raise ValueError("Проект не найден")

        if project.owner_id != user_id:
            raise PermissionError("Вы не являетесь владельцем этого проекта")

        if project.status != "draft":
            raise ValueError("Открыть можно только проекты в статусе черновика")

        return await self.project_repository.update_status(project, "open")

    async def close_project(self, project_id: int, user_id: int):
        project = await self.project_repository.get_by_id(project_id)

        if not project:
            raise ValueError("Проект не найден")

        if project.owner_id != user_id:
            raise PermissionError("Вы не являетесь владельцем этого проекта")

        if project.status != "open":
            raise ValueError("Закрыть можно только открытый проект")

        return await self.project_repository.update_status(project, "closed")

    async def delete_project(self, project_id: int, user_id: int):
        project = await self.project_repository.get_by_id(project_id)

        if not project:
            raise ValueError("Проект не найден")

        if project.owner_id != user_id:
            raise PermissionError("Вы не являетесь владельцем проекта")

        await self.project_repository.delete_project(project)

    async def get_project_by_id(self, project_id: int):
        return await self.project_repository.get_by_id(project_id)

    async def update_project(
        self,
        project_id: int,
        user_id: int,
        title: str,
        description: str,
        max_participants: int,
    ):
        project = await self.project_repository.get_by_id(project_id)

        if not project:
            raise ValueError("Проект не найден")

        if project.owner_id != user_id:
            raise PermissionError("Вы не являетесь владельцем проекта")

        if project.status != "draft":
            raise ValueError("Редактировать можно только проект в статусе черновика")

        if max_participants <= 0:
            raise ValueError("Количество участников должно быть больше 0")

        return await self.project_repository.update_project(
            project=project,
            title=title,
            description=description,
            max_participants=max_participants,
        )
