from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.Proyectos.repository import ProyectoRepository
from app.api.v1.Proyectos.schemas import ProyectoCreate, ProyectoResponse
from app.core.db import get_db

router = APIRouter(
    prefix="/proyectos",
    tags=["proyectos"],
    responses={404: {"description": "Not found"}},
)

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
):
    repo = ProyectoRepository(db)

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