from fastapi import FastAPI, Request
from router.modelRoutes import video
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

curr_path = os.path.join(os.getcwd(), "template")
templates = Jinja2Templates(directory=curr_path)


@app.get("/")
async def Welcome(request: Request):
    # print(os.listdir('./app/'))
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(video)
