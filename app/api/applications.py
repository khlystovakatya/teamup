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

    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    application_repository = ApplicationRepository(session)
    application_service = ApplicationService(application_repository)

    applications = await application_service.get_project_applications(project_id)

    return templates.TemplateResponse(
        request=request,
        name="project_applications.html",
        context={
            "applications": applications,
            "project_id": project_id,
        }
    )


@router.post("/applications/{application_id}/accept")
async def accept_application(
    application_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")

    application_repository = ApplicationRepository(session)
    application_service = ApplicationService(application_repository)

    try:
        await application_service.change_status(application_id, user_id, "accepted")
    except ValueError:
        pass

    return RedirectResponse(url="/my-projects", status_code=303)


@router.post("/applications/{application_id}/reject")
async def reject_application(
    application_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    user_id = request.session.get("user_id")

    application_repository = ApplicationRepository(session)
    application_service = ApplicationService(application_repository)

    try:
        await application_service.change_status(application_id, user_id, "rejected")
    except ValueError:
        pass

    return RedirectResponse(url="/my-projects", status_code=303)
