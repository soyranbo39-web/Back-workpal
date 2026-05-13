import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.uploads.router import router as upload_router
from app.api.v1.auth.router import auth_router
from app.api.v1.Alumnos.router import router as post_router

from app.core.db import Base, engine

load_dotenv()


MEDIA_DIR= "app/media"


def create_app()-> FastAPI:
    app = FastAPI(title="Workpal API", version="1.0")
    Base.metadata.create_all(bind=engine)  # dev
    app.include_router(auth_router,prefix="/api/v1")
    app.include_router(post_router)
    app.include_router(upload_router)
  
    
    os.makedirs(MEDIA_DIR, exist_ok=True)
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
    return app

app = create_app()

