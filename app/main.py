import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.uploads.router import router as upload_router
from app.api.v1.auth.router import auth_router
from app.api.v1.Alumnos.router import router as alumno_router
from app.api.v1.Proyectos.router import router as proyectos_router
from app.api.v1.Tareas.router import router as tareas_router

from app.core.db import Base, engine

load_dotenv()


MEDIA_DIR= "app/media"


def create_app()-> FastAPI:
    app = FastAPI(title="Workpal API", version="1.0")

    cors_origins = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOW_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Base.metadata.create_all(bind=engine)  # dev
    app.include_router(auth_router,prefix="/api/v1")
    app.include_router(alumno_router,prefix="/api/v1")
    app.include_router(proyectos_router, prefix="/api/v1")
    app.include_router(tareas_router, prefix="/api/v1")
    app.include_router(upload_router)
  
    
    os.makedirs(MEDIA_DIR, exist_ok=True)
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
    return app

app = create_app()

