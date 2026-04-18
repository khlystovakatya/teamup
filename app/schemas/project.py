from pydantic import BaseModel


class ProjectCreate(BaseModel):
    title: str
    description: str


class ProjectRead(BaseModel):
    id: int
    title: str
    description: str
    status: str
    owner_id: int
