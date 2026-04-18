from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    async def create_project(self, project_data: ProjectCreate, owner_id: int):
        return await self.project_repository.create_project(
            title=project_data.title,
            description=project_data.description,
            owner_id=owner_id
        )

    async def get_all_projects(self):
        return await self.project_repository.get_all_projects()