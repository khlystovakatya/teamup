from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.repositories.application_repository import ApplicationRepository
from app.services.application_service import ApplicationService

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/projects/{project_id}/apply")
async def apply_to_project(
    project_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    application_repository = ApplicationRepository(session)
    application_service = ApplicationService(application_repository)

    try:
        await application_service.apply_to_project(project_id=project_id, user_id=user_id)
        return RedirectResponse(
            url="/projects?message=Вы успешно откликнулись на проект", 
            status_code=303,
        )
    except ValueError as e:
        return RedirectResponse(
            url=f"/projects?message={str(e)}", 
            status_code=303,
        )


@router.get("/my-applications")
async def my_applications(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    application_repository = ApplicationRepository(session)
    application_service = ApplicationService(application_repository)

    applications = await application_service.get_user_applications(user_id)

    user_name = request.session.get("user_name")
    user_email = request.session.get("user_email")

    return templates.TemplateResponse(
        request=request,
        name="my_applications.html",
        context={
            "applications": applications,
            "user_name": user_name,
            "user_email": user_email
        }
    )


@router.get("/projects/{project_id}/applications")
async def project_applications(
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

    application_repository = ApplicationRepository(session)
    application_service = ApplicationService(application_repository)

    project = await application_repository.get_project_by_id(project_id)

    if not project:
        return RedirectResponse(
            url="/my-projects?message=Проект не найден", 
            status_code=303
        )

    if project.owner_id != user_id:
        return RedirectResponse(
            url="/my-projects?message=У вас нет доступа к откликам на этот проект", 
            status_code=303
        )

    applications = await application_service.get_project_applications(project_id)
    message = request.query_params.get("message")

    return templates.TemplateResponse(
        request=request,
        name="project_applications.html",
        context={
            "project": project,
            "applications": applications,
            "user_name": user_name,
            "user_email": user_email,
            "user_role": user_role,
            "message": message
        }
    )


@router.post("/applications/{application_id}/accept")
async def accept_application(
    application_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    application_repository = ApplicationRepository(session)
    application_service = ApplicationService(application_repository)

    application = await application_repository.get_by_id(application_id)

    if not application:
        return RedirectResponse(url="/my-projects", status_code=303)

    project_id = application.project_id

    try:
        await application_service.change_status(
            application_id=application_id, 
            user_id=user_id, 
            status="accepted",
        )

        return RedirectResponse(
            url=f"/projects/{project_id}/applications?message=Отклик принят", 
            status_code=303,
        )

    except ValueError as e:
        return RedirectResponse(
            url=f"/projects/{project_id}/applications?message={str(e)}", 
            status_code=303,
        )


@router.post("/applications/{application_id}/reject")
async def reject_application(
    application_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    application_repository = ApplicationRepository(session)
    application_service = ApplicationService(application_repository)

    application = await application_repository.get_by_id(application_id)

    if not application:
        return RedirectResponse(url="/my-projects", status_code=303)

    project_id = application.project_id

    try:
        await application_service.change_status(
            application_id=application_id, 
            user_id=user_id, 
            status="rejected",
        )

        return RedirectResponse(
            url=f"/projects/{project_id}/applications?message=Отклик отклонен", 
            status_code=303,
        )

    except ValueError as e:
        return RedirectResponse(
            url=f"/projects/{project_id}/applications?message={str(e)}", 
            status_code=303,
        )
