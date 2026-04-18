from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
def main_page(request: Request):
    user_name = request.session.get("user_name")
    user_email = request.session.get("user_email")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user_name": user_name,
            "user_email": user_email,
        }
    )


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"error": None}
    )


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": None}
    )