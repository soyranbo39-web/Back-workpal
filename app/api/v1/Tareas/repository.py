from sqlalchemy.orm import Session
from app.models.Tareas import Tarea
from app.api.v1.Tareas.schemas import TareaCreate, TareaUpdateStatus
from app.models.Alumnos import Alumno

class TareaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_tarea(self, proyecto_id: int, tarea_data: TareaCreate) -> Tarea:
        new_tarea = Tarea(
            proyecto_id=proyecto_id,
            assigned_to=tarea_data.assigned_to,
            title=tarea_data.title,
            description=tarea_data.description,
            end_date=tarea_data.end_date,
            status="Pendiente"
        )
        self.db.add(new_tarea)
        return new_tarea

    def get_tareas_by_proyecto(self, proyecto_id: int) -> list[Tarea]:
        return self.db.query(Tarea).filter(Tarea.proyecto_id == proyecto_id).all()

    def get_tareas_by_proyecto_and_alumno(self, proyecto_id: int, alumno_id: int) -> list[Tarea]:
        return self.db.query(Tarea).filter(
            Tarea.proyecto_id == proyecto_id,
            Tarea.assigned_to == alumno_id
        ).all()

    def get_tarea_by_id(self, tarea_id: int) -> Tarea | None:
        return self.db.query(Tarea).filter(Tarea.id == tarea_id).first()

    def update_tarea_status(self, tarea: Tarea, new_status: str) -> Tarea:
        tarea.status = new_status
        return tarea
