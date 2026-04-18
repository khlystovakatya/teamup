from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.repositories.project_repository import ProjectRepository
from app.repositories.application_repository import ApplicationRepository
from app.schemas.project import ProjectCreate
from app.services.project_service import ProjectService
from app.services.application_service import ApplicationService

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/projects")
async def projects_list(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    project_repository = ProjectRepository(session)
    project_service = ProjectService(project_repository)

    projects = await project_service.get_all_projects()

    user_name = request.session.get("user_name")
    user_email = request.session.get("user_email")
    user_id = request.session.get("user_id")

    message = request.query_params.get("message")

    applied_project_ids = set()
    if user_id:
        application_repository = ApplicationRepository(session)
        application_service = ApplicationService(application_repository)
        applied_project_ids = await application_service.get_user_project_ids_with_applications(user_id)

    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={
            "projects": projects,
            "user_name": user_name,
            "user_email": user_email,
            "user_id": user_id,
            "applied_project_ids": applied_project_ids,
            "message": message,
        }
    )


@router.get("/projects/create")
def create_project_page(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="create_project.html",
        context={"error": None}
    )


@router.post("/projects/create")
async def create_project(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    project_repository = ProjectRepository(session)
    project_service = ProjectService(project_repository)

    project_data = ProjectCreate(
        title=title,
        description=description,
    )

    await project_service.create_project(project_data, owner_id=user_id)

    return RedirectResponse(url="/projects?message=Проект успешно создан", status_code=303)