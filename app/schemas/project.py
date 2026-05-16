from pydantic import BaseModel


class ProjectCreate(BaseModel):
    title: str
    description: str
    max_participants: int


class ProjectRead(BaseModel):
    id: int
    title: str
    description: str
    status: str
    max_participants: int
    owner_id: int
