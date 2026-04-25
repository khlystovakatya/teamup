from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_user(self, user_data: UserCreate):
        existing_user = await self.user_repository.get_by_email(user_data.email)

        if existing_user:
            raise ValueError("Пользователь с таким email уже существует")

        return await self.user_repository.create_user(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role,
        )