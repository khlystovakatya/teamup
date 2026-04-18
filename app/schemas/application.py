from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    project_id: int
    user_id: int


class ApplicationRead(BaseModel):
    id: int
    project_id: int
    user_id: int
    status: str