from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.sessions import SessionMiddleware

from app.db import engine, Base, get_session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.services.user_service import UserService

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

templates = Jinja2Templates(directory="templates")


# создаем таблицы при запуске приложения
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# главная страница
@app.get("/")
def main_page(request: Request):
    user_name = request.session.get("user_name")
    user_email = request.session.get("user_email")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user_name": user_name,
            "user_email": user_email
        }
    )


# страница регистрации
@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"error": None}
    )


@app.post("/register")
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
        user_data = UserCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )

        await user_service.register_user(user_data)

        return RedirectResponse(url="/login", status_code=303)

    except ValueError as e:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": str(e)},
        )


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": None}
    )


@app.post("/login")
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

    return RedirectResponse(url="/", status_code=303)


@app.get("/logout")
def logout_user(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)