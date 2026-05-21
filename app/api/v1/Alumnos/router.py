
from typing import Annotated, Optional, cast

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.Alumnos.repository import AlumnoRepository
from app.core.db import get_db
from app.core.security import get_current_user
from app.services.file_storage import save_uploaded_image

from .schemas import AlumnoCreate, AlumnoResponse

router = APIRouter(
    prefix="/alumnos",
    tags=["alumnos"],
    responses={404: {"description": "Not found"}},
)
@router.get("/{alumno_id}", response_model=AlumnoResponse)
async def get_alumno(alumno_id: int, db: Annotated[Session, Depends(get_db)]):
    repo = AlumnoRepository(db)
    alumno = repo.get_alumno_by_id(alumno_id)
    if alumno is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alumno no encontrado")
    return alumno


@router.get("/", response_model=list[AlumnoResponse])
async def list_alumnos(db: Annotated[Session, Depends(get_db)]):
    repo = AlumnoRepository(db)
    return repo.list_alumnos()



@router.post("/", response_model=AlumnoResponse)
async def create_alumno(
    alumno: Annotated[AlumnoCreate, Depends(AlumnoCreate.as_form)],
    imagen: Annotated[Optional[UploadFile], File()] = None,
    db: Annotated[Session, Depends(get_db)] = None,
    user: Annotated[dict, Depends(get_current_user)] = None,
):
    repo = AlumnoRepository(db)
    saved : Optional[dict[str, str]] = None
    try:
        if imagen is not None:
            saved = cast(dict[str, str], save_uploaded_image(imagen))
        
        imagen_url : str = saved["url"] if saved is not None else ""
        if alumno.name is None : 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El campo 'name' es obligatorio")
        
        created_post = repo.create_alumno(
            AlumnoCreate(
                name=alumno.name,
                last_name=alumno.last_name,
                carrera=alumno.carrera,
                imagen_url=imagen_url
            ),
            user_id=user
        )
        db.commit()
        db.refresh(created_post)
        return created_post
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alumno con el mismo ID ya existe")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el alumno")
        
            
@router.delete("/{alumno_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alumno(alumno_id: int, db: Annotated[Session, Depends(get_db)]):
    repo = AlumnoRepository(db)
    alumno = repo.get_alumno_by_id(alumno_id)
    if alumno is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alumno no encontrado")
    repo.delete_alumno(alumno)
    db.commit()

@router.put("/{alumno_id}", response_model=AlumnoResponse)
async def update_alumno(
    alumno_id: int,
    alumno_data: Annotated[AlumnoCreate, Depends(AlumnoCreate.as_form)],
    imagen: Annotated[Optional[UploadFile], File()] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    repo = AlumnoRepository(db)
    alumno = repo.get_alumno_by_id(alumno_id)
    if alumno is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alumno no encontrado")
    
    try:
        if imagen is not None:
            saved = cast(dict[str, str], save_uploaded_image(imagen))
            alumno_data.imagen_url = saved["url"]
        
        updated_alumno = repo.update_alumno(alumno, alumno_data)
        db.commit()
        db.refresh(updated_alumno)
        return updated_alumno
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alumno con el mismo ID ya existe")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el alumno")
    
