from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user
from app.api.v1.Tareas.schemas import TareaCreate, TareaResponse, TareaUpdateStatus
from app.api.v1.Tareas.repository import TareaRepository
from app.api.v1.Proyectos.repository import ProyectoRepository
from app.api.v1.Alumnos.repository import AlumnoRepository

router = APIRouter(
    prefix="/proyectos",
    tags=["tareas"],
)

@router.post("/{proyecto_id}/tareas", response_model=TareaResponse)
async def create_tarea(
    proyecto_id: int,
    tarea_data: TareaCreate,
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Depends(get_current_user)]
):
    alumno_repo = AlumnoRepository(db)
    me = alumno_repo.get_alumno_by_user_id(user_id)
    if not me:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    proy_repo = ProyectoRepository(db)
    proyecto = proy_repo.get_proyecto_by_id(proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    if proyecto.owner_id != me.id:
        raise HTTPException(status_code=403, detail="Solo el administrador puede crear tareas")

    tarea_repo = TareaRepository(db)
    new_tarea = tarea_repo.create_tarea(proyecto_id, tarea_data)
    db.commit()
    db.refresh(new_tarea)
    
    # Add responsable name for response
    resp = alumno_repo.get_alumno_by_id(new_tarea.assigned_to)
    res_data = TareaResponse.from_orm(new_tarea)
    res_data.responsable_name = f"{resp.name} {resp.last_name}" if resp else "Desconocido"
    return res_data

@router.get("/{proyecto_id}/tareas", response_model=list[TareaResponse])
async def list_tareas(
    proyecto_id: int,
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Depends(get_current_user)]
):
    alumno_repo = AlumnoRepository(db)
    me = alumno_repo.get_alumno_by_user_id(user_id)
    if not me:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    proy_repo = ProyectoRepository(db)
    proyecto = proy_repo.get_proyecto_by_id(proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    tarea_repo = TareaRepository(db)
    
    # If admin, see all. If collaborator, see only theirs.
    if proyecto.owner_id == me.id:
        tareas = tarea_repo.get_tareas_by_proyecto(proyecto_id)
    else:
        # Check if collaborator
        colabs = proy_repo.get_collaborators_by_project(proyecto_id)
        is_colab = any(c.alumno_id == me.id for c in colabs)
        if not is_colab:
            raise HTTPException(status_code=403, detail="No eres colaborador de este proyecto")
        tareas = tarea_repo.get_tareas_by_proyecto_and_alumno(proyecto_id, me.id)

    result = []
    for t in tareas:
        resp = alumno_repo.get_alumno_by_id(t.assigned_to)
        tr = TareaResponse.from_orm(t)
        tr.responsable_name = f"{resp.name} {resp.last_name}" if resp else "Desconocido"
        result.append(tr)
    return result

@router.put("/tareas/{tarea_id}/status", response_model=TareaResponse)
async def update_tarea_status(
    tarea_id: int,
    status_data: TareaUpdateStatus,
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str, Depends(get_current_user)]
):
    alumno_repo = AlumnoRepository(db)
    me = alumno_repo.get_alumno_by_user_id(user_id)
    if not me:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    tarea_repo = TareaRepository(db)
    tarea = tarea_repo.get_tarea_by_id(tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    proy_repo = ProyectoRepository(db)
    proyecto = proy_repo.get_proyecto_by_id(tarea.proyecto_id)
    
    is_admin = proyecto.owner_id == me.id
    is_assigned = tarea.assigned_to == me.id
    
    new_status = status_data.status
    allowed_statuses = ["Pendiente", "En Proceso", "Completada", "Confirmada"]
    if new_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Estado no válido")

    # Workflow logic
    if is_assigned and not is_admin:
        # Collaborator rules
        if new_status == "Confirmada":
            raise HTTPException(status_code=403, detail="Solo el administrador puede confirmar tareas")
        
        # Valid transitions: Pendiente -> En Proceso -> Completada
        if tarea.status == "Pendiente" and new_status != "En Proceso":
             raise HTTPException(status_code=400, detail="De Pendiente solo puedes pasar a En Proceso")
        if tarea.status == "En Proceso" and new_status != "Completada":
             raise HTTPException(status_code=400, detail="De En Proceso solo puedes pasar a Completada")
        if tarea.status == "Completada":
             raise HTTPException(status_code=400, detail="Tarea ya completada, espera confirmación")
        if tarea.status == "Confirmada":
             raise HTTPException(status_code=400, detail="Tarea ya confirmada")

    elif is_admin:
        # Admin rules
        if is_assigned:
            # Admin's own tasks: can go to any status? User said: "el administrador tendrá 4 opciones en total para el estado de la tarea (Pendiente, En Proceso, Completada, Confirmada)"
            # Let's allow admin to move their own tasks through all.
            pass
        else:
            # Admin confirming collaborator's task
            if new_status != "Confirmada":
                raise HTTPException(status_code=400, detail="El administrador solo puede confirmar tareas de otros")
            if tarea.status != "Completada":
                raise HTTPException(status_code=400, detail="Solo se pueden confirmar tareas completadas")
    else:
        raise HTTPException(status_code=403, detail="No tienes permiso sobre esta tarea")

    tarea_repo.update_tarea_status(tarea, new_status)
    db.commit()
    db.refresh(tarea)
    
    resp = alumno_repo.get_alumno_by_id(tarea.assigned_to)
    tr = TareaResponse.from_orm(tarea)
    tr.responsable_name = f"{resp.name} {resp.last_name}" if resp else "Desconocido"
    return tr
