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
            owner_id=owner_id
        )

    async def get_all_projects(self):
        return await self.project_repository.get_all_projects()

    def get_accepted_count(self, project: Project) -> int:
        return len([
            application
            for application in project.applications
            if application.status == "accepted"
        ])

    def get_free_slots(self, project: Project) -> int:
        accepted_count = self.get_accepted_count(project)
        return project.max_participants - accepted_count