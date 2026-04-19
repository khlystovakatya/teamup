from app.repositories.application_repository import ApplicationRepository


class ApplicationService:
    def __init__(self, application_repository: ApplicationRepository):
        self.application_repository = application_repository

    async def apply_to_project(self, project_id: int, user_id: int):
        project = await self.application_repository.get_project_by_id(project_id)

        if project is None:
            raise ValueError("Проект не найден")

        if project.owner_id == user_id:
            raise ValueError("Нельзя откликнуться на собственный проект")

        existing_application = await self.application_repository.get_by_project_and_user(
            project_id=project_id, 
            user_id=user_id,
        )  

        if existing_application:
            raise ValueError("Вы уже откликались на этот проект")

        return await self.application_repository.create_application(
            project_id=project_id, 
            user_id=user_id,
        )

    async def get_user_applications(self, user_id: int):
        return await self.application_repository.get_user_applications(user_id)

    async def get_user_project_ids_with_applications(self, user_id: int) -> set[int]:
        return await self.application_repository.get_user_project_ids_with_applications(user_id)

    async def change_status(self, application_id: int, user_id: int, status: str):
        application = await self.application_repository.get_by_id(application_id)

        if not application:
            raise ValueError("Отклик не найден")

        project = await self.application_repository.get_project_by_id(application.project_id)

        if project.owner_id != user_id:
            raise ValueError("Вы не являетесь владельцем проекта")

        if application.status != "pending":
            raise ValueError("Статус уже изменен")

        return await self.application_repository.update_status(application, status)

    async def get_project_applications(self, project_id: int):
        return await self.application_repository.get_project_applications(project_id)