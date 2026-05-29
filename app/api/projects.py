from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.repositories.application_repository import ApplicationRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate
from app.services.application_service import ApplicationService
from app.services.project_service import ProjectService

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

    user_id = request.session.get("user_id")
    user_name = request.session.get("user_name")
    user_email = request.session.get("user_email")
    user_role = request.session.get("user_role")

    message = request.query_params.get("message")

    applied_project_ids = set()

    if user_id:
        application_repository = ApplicationRepository(session)
        application_service = ApplicationService(application_repository)

        applied_project_ids = (
            await application_service.get_user_project_ids_with_applications(user_id)
        )

    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={
            "projects": projects,
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email,
            "user_role": user_role,
            "applied_project_ids": applied_project_ids,
            "message": message,
        },
    )


@router.get("/projects/create")
def create_project_page(request: Request):
    user_id = request.session.get("user_id")
    user_name = request.session.get("user_name")
    user_email = request.session.get("user_email")
    user_role = request.session.get("user_role")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="create_project.html",
        context={
            "error": None,
            "user_name": user_name,
            "user_email": user_email,
            "user_role": user_role,
        },
    )


@router.post("/projects/create")
async def create_project(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    max_participants: int = Form(...),
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")
    user_name = request.session.get("user_name")
    user_email = request.session.get("user_email")
    user_role = request.session.get("user_role")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    project_repository = ProjectRepository(session)
    project_service = ProjectService(project_repository)

    try:
        project_data = ProjectCreate(
            title=title,
            description=description,
            max_participants=max_participants,
        )

        await project_service.create_project(project_data, owner_id=user_id)

        return RedirectResponse(
            url="/projects?message=Проект успешно создан",
            status_code=303,
        )

    except ValueError as e:
        return templates.TemplateResponse(
            request=request,
            name="create_project.html",
            context={
                "error": str(e),
                "user_name": user_name,
                "user_email": user_email,
                "user_role": user_role,
            },
        )


@router.get("/projects/{project_id}")
async def project_detail(
    project_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    project_repository = ProjectRepository(session)
    project_service = ProjectService(project_repository)

    project = await project_service.get_project_by_id(project_id)

    if not project:
        return RedirectResponse(
            url="/projects?message=Проект не найден",
            status_code=303,
        )

    user_id = request.session.get("user_id")
    user_name = request.session.get("user_name")
    user_email = request.session.get("user_email")
    user_role = request.session.get("user_role")

    accepted_count = project_service.get_accepted_count(project)
    free_slots = project_service.get_free_slots(project)

    already_applied = False

    if user_id:
        application_repository = ApplicationRepository(session)
        existing_application = await application_repository.get_by_project_and_user(
            project_id=project.id,
            user_id=user_id,
        )

        already_applied = existing_application is not None

    message = request.query_params.get("message")

    return templates.TemplateResponse(
        request=request,
        name="project_detail.html",
        context={
            "project": project,
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email,
            "user_role": user_role,
            "accepted_count": accepted_count,
            "free_slots": free_slots,
            "already_applied": already_applied,
            "message": message,
        },
    )


@router.get("/projects/{project_id}/edit")
async def edit_project_page(
    project_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")
    user_name = request.session.get("user_name")
    user_email = request.session.get("user_email")
    user_role = request.session.get("user_role")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    project_repository = ProjectRepository(session)
    project_service = ProjectService(project_repository)

    project = await project_service.get_project_by_id(project_id)

    if not project:
        return RedirectResponse(
            url="/my-projects?message=Проект не найден",
            status_code=303,
        )

    if project.owner_id != user_id:
        return RedirectResponse(
            url="/my-projects?message=Вы не являетесь владельцем этого проекта",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_project.html",
        context={
            "project": project,
            "error": None,
            "user_name": user_name,
            "user_email": user_email,
            "user_role": user_role,
        },
    )


@router.post("/projects/{project_id}/edit")
async def edit_project(
    project_id: int,
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    max_participants: int = Form(...),
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")
    user_name = request.session.get("user_name")
    user_email = request.session.get("user_email")
    user_role = request.session.get("user_role")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    project_repository = ProjectRepository(session)
    project_service = ProjectService(project_repository)

    try:
        project = await project_service.update_project(
            project_id=project_id,
            user_id=user_id,
            title=title,
            description=description,
            max_participants=max_participants,
        )

        return RedirectResponse(
            url=f"/projects/{project_id}?message=Проект успешно обновлен",
            status_code=303,
        )

    except ValueError as e:
        project = await project_service.get_project_by_id(project_id)

        return templates.TemplateResponse(
            request=request,
            name="edit_project.html",
            context={
                "project": project,
                "error": str(e),
                "user_name": user_name,
                "user_email": user_email,
                "user_role": user_role,
            },
        )


@router.get("/my-projects")
async def my_projects(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")
    user_name = request.session.get("user_name")
    user_email = request.session.get("user_email")
    user_role = request.session.get("user_role")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    project_repository = ProjectRepository(session)
    project_service = ProjectService(project_repository)

    projects = await project_service.get_all_projects()
    user_projects = [project for project in projects if project.owner_id == user_id]

    message = request.query_params.get("message")

    return templates.TemplateResponse(
        request=request,
        name="my_projects.html",
        context={
            "projects": user_projects,
            "user_name": user_name,
            "user_email": user_email,
            "user_role": user_role,
            "message": message,
        },
    )


@router.get("/admin/projects")
async def admin_projects(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    user_role = request.session.get("user_role")
    user_name = request.session.get("user_name")
    user_email = request.session.get("user_email")

    if user_role != "admin":
        return RedirectResponse(url="/", status_code=303)

    project_repository = ProjectRepository(session)
    project_service = ProjectService(project_repository)

    projects = await project_service.get_all_projects()

    return templates.TemplateResponse(
        request=request,
        name="admin_projects.html",
        context={
            "projects": projects,
            "user_name": user_name,
            "user_email": user_email,
            "user_role": user_role,
        },
    )


@router.post("/projects/{project_id}/open")
async def open_project(
    project_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    project_repository = ProjectRepository(session)
    project_service = ProjectService(project_repository)

    try:
        await project_service.open_project(project_id=project_id, user_id=user_id)

        return RedirectResponse(
            url="/my-projects?message=Проект открыт для откликов",
            status_code=303,
        )

    except ValueError as e:
        return RedirectResponse(
            url=f"/my-projects?message={str(e)}",
            status_code=303,
        )


@router.post("/projects/{project_id}/close")
async def close_project(
    project_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    project_repository = ProjectRepository(session)
    project_service = ProjectService(project_repository)

    try:
        await project_service.close_project(project_id=project_id, user_id=user_id)

        return RedirectResponse(
            url="/my-projects?message=Проект закрыт",
            status_code=303,
        )

    except ValueError as e:
        return RedirectResponse(
            url=f"/my-projects?message={str(e)}",
            status_code=303,
        )


@router.post("/projects/{project_id}/delete")
async def delete_project(
    project_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    project_repository = ProjectRepository(session)
    project_service = ProjectService(project_repository)

    try:
        await project_service.delete_project(project_id=project_id, user_id=user_id)

        return RedirectResponse(
            url="/my-projects?message=Проект удален",
            status_code=303,
        )

    except ValueError as e:
        return RedirectResponse(
            url=f"/my-projects?message={str(e)}",
            status_code=303,
        )
