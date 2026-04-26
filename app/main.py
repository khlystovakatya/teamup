from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.auth import router as auth_router
from app.api.pages import router as pages_router
from app.api.projects import router as projects_router
from app.api.applications import router as applications_router
from app.db import engine, Base
from app.models.user import User
from app.models.project import Project
from app.models.application import Application

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(SessionMiddleware, secret_key="super-secret-key")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(applications_router)