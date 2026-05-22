from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.Proyectos.repository import ProyectoRepository
from app.api.v1.Alumnos.repository import AlumnoRepository
from app.api.v1.Proyectos.schemas import ProyectoCreate, ProyectoResponse, ProyectoAlumnoResponse
from app.core.db import get_db
from app.core.security import get_current_user

router = APIRouter(
    prefix="/proyectos",
    tags=["proyectos"],
    responses={404: {"description": "Not found"}},
)

@router.get("/mis-proyectos", response_model=list[ProyectoResponse])
async def list_mis_proyectos(
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Depends(get_current_user)]
):
    alumno_repo = AlumnoRepository(db)
    alumno = alumno_repo.get_alumno_by_user_id(user_id)
    if not alumno:
        raise HTTPException(status_code=404, detail="Perfil de alumno no encontrado")
    
    repo = ProyectoRepository(db)
    return repo.list_proyectos_by_owner(alumno.id)

@router.get("/{proyecto_id}", response_model=ProyectoResponse)
async def get_proyecto(
    proyecto_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    repo = ProyectoRepository(db)
    proyecto = repo.get_proyecto_by_id(proyecto_id)

    if proyecto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    return proyecto

@router.get("/", response_model=list[ProyectoResponse])
async def list_proyectos(
    db: Annotated[Session, Depends(get_db)]
):
    repo = ProyectoRepository(db)
    return repo.list_proyectos()

@router.post("/", response_model=ProyectoResponse)
async def create_proyecto(
    proyecto: ProyectoCreate,
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Depends(get_current_user)]
):
    alumno_repo = AlumnoRepository(db)
    alumno = alumno_repo.get_alumno_by_user_id(user_id)
    if not alumno:
        raise HTTPException(status_code=404, detail="Perfil de alumno no encontrado")

    repo = ProyectoRepository(db)
    proyecto.owner_id = alumno.id

    try:
        created_proyecto = repo.create_proyecto(proyecto)

        db.commit()
        db.refresh(created_proyecto)

        return created_proyecto

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad"
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el proyecto"
        )

@router.post("/{proyecto_id}/aplicar", response_model=ProyectoAlumnoResponse)
async def aplicar_a_proyecto(
    proyecto_id: int,
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Depends(get_current_user)]
):
    alumno_repo = AlumnoRepository(db)
    alumno = alumno_repo.get_alumno_by_user_id(user_id)
    if not alumno:
        raise HTTPException(status_code=404, detail="Perfil de alumno no encontrado")

    repo = ProyectoRepository(db)
    proyecto = repo.get_proyecto_by_id(proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    if proyecto.owner_id == alumno.id:
        raise HTTPException(status_code=400, detail="No puedes aplicar a tu propio proyecto")

    try:
        application = repo.apply_to_project(proyecto_id, alumno.id)
        db.commit()
        db.refresh(application)
        return application
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ya has aplicado a este proyecto")

@router.get("/{proyecto_id}/aplicaciones", response_model=list[dict])
async def list_aplicaciones(
    proyecto_id: int,
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Depends(get_current_user)]
):
    repo = ProyectoRepository(db)
    proyecto = repo.get_proyecto_by_id(proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    alumno_repo = AlumnoRepository(db)
    me_alumno = alumno_repo.get_alumno_by_user_id(user_id)
    if not me_alumno or proyecto.owner_id != me_alumno.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver las aplicaciones de este proyecto")

    # Get applications and join with Alumno to get their names
    apps = repo.get_applications_by_project(proyecto_id)
    result = []
    for app in apps:
        app_alumno = alumno_repo.get_alumno_by_id(app.alumno_id)
        result.append({
            "id": app.id,
            "proyecto_id": app.proyecto_id,
            "alumno_id": app.alumno_id,
            "status": app.status,
            "alumno_name": f"{app_alumno.name} {app_alumno.last_name}" if app_alumno else "Desconocido",
            "alumno_carrera": app_alumno.carrera if app_alumno else ""
        })
    return result

@router.get("/{proyecto_id}/colaboradores", response_model=list[dict])
async def list_colaboradores(
    proyecto_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    repo = ProyectoRepository(db)
    proyecto = repo.get_proyecto_by_id(proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    alumno_repo = AlumnoRepository(db)
    colabs = repo.get_collaborators_by_project(proyecto_id)
    result = []
    for col in colabs:
        col_alumno = alumno_repo.get_alumno_by_id(col.alumno_id)
        result.append({
            "id": col.id,
            "alumno_id": col.alumno_id,
            "alumno_name": f"{col_alumno.name} {col_alumno.last_name}" if col_alumno else "Desconocido",
            "alumno_carrera": col_alumno.carrera if col_alumno else "",
            "imagen_url": col_alumno.imagen_url if col_alumno else ""
        })
    return result

@router.post("/aplicaciones/{application_id}/aceptar", response_model=ProyectoAlumnoResponse)
async def aceptar_aplicacion(
    application_id: int,
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Depends(get_current_user)]
):
    repo = ProyectoRepository(db)
    application = repo.get_application_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Aplicación no encontrada")
    
    proyecto = repo.get_proyecto_by_id(application.proyecto_id)
    alumno_repo = AlumnoRepository(db)
    alumno = alumno_repo.get_alumno_by_user_id(user_id)
    
    if not alumno or proyecto.owner_id != alumno.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para aceptar aplicaciones en este proyecto")

    repo.update_application_status(application, "accepted")
    db.commit()
    db.refresh(application)
    return application

@router.post("/aplicaciones/{application_id}/rechazar", response_model=ProyectoAlumnoResponse)
async def rechazar_aplicacion(
    application_id: int,
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Depends(get_current_user)]
):
    repo = ProyectoRepository(db)
    application = repo.get_application_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Aplicación no encontrada")
    
    proyecto = repo.get_proyecto_by_id(application.proyecto_id)
    alumno_repo = AlumnoRepository(db)
    alumno = alumno_repo.get_alumno_by_user_id(user_id)
    
    if not alumno or proyecto.owner_id != alumno.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para rechazar aplicaciones en este proyecto")

    repo.update_application_status(application, "rejected")
    db.commit()
    db.refresh(application)
    return application

@router.put("/{proyecto_id}", response_model=ProyectoResponse)
async def update_proyecto(
    proyecto_id: int,
    proyecto_data: ProyectoCreate,
    db: Annotated[Session, Depends(get_db)],
):
    repo = ProyectoRepository(db)
    proyecto = repo.get_proyecto_by_id(proyecto_id)

    if proyecto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    try:
        updated_proyecto = repo.update_proyecto(
            proyecto,
            proyecto_data
        )

        db.commit()
        db.refresh(updated_proyecto)

        return updated_proyecto

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad"
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el proyecto"
        )

@router.delete("/{proyecto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proyecto(
    proyecto_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    repo = ProyectoRepository(db)
    proyecto = repo.get_proyecto_by_id(proyecto_id)

    if proyecto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )

    repo.delete_proyecto(proyecto)
    db.commit()