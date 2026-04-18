from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, name: str, email: str, password: str) -> User:
        user = User(name=name, email=email, password=password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user