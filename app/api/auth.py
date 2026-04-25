from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.services.user_service import UserService

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/register")
async def register_user(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    user_repository = UserRepository(session)
    user_service = UserService(user_repository)

    try:
        role = "admin" if email == "admin@example.com" else "user"

        user_data = UserCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=role,
        )

        await user_service.register_user(user_data)

        return RedirectResponse(url="/login", status_code=303)

    except ValueError as e:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": str(e)},
        )


@router.post("/login")
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    user_repository = UserRepository(session)

    user = await user_repository.get_by_email(email)

    if user is None or user.password != password:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Неверный email или пароль"},
        )

    request.session["user_id"] = user.id
    request.session["user_name"] = f"{user.first_name} {user.last_name}"
    request.session["user_email"] = user.email
    request.session["user_role"] = user.role

    return RedirectResponse(url="/", status_code=303)


@router.get("/logout")
def logout_user(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)