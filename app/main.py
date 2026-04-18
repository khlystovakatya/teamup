from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from app.db import engine, Base

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# создаем таблицы при запуске приложения
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# главная страница
@app.get("/")
def main_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )