from sqlalchemy.orm import Session

from app.api.v1.Proyectos.schemas import ProyectoCreate
from app.models.Proyectos import Proyecto
from app.models.Proyecto_Alumnos import ProyectoAlumno


class ProyectoRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_proyecto(self, proyecto: ProyectoCreate) -> Proyecto:
        new_proyecto = Proyecto(
            name=proyecto.name,
            skill=proyecto.skill,
            description=proyecto.description,
            start=proyecto.start,
            end=proyecto.end,
            image=proyecto.image,
            owner_id=proyecto.owner_id
        )
        self.db.add(new_proyecto)
        return new_proyecto

    def get_proyecto_by_id(self, proyecto_id: int) -> Proyecto | None:
        return (
            self.db.query(Proyecto)
            .filter(Proyecto.id == proyecto_id)
            .first()
        )

    def list_proyectos(self) -> list[Proyecto]:
        return self.db.query(Proyecto).all()

    def list_proyectos_by_owner(self, owner_id: int) -> list[Proyecto]:
        return (
            self.db.query(Proyecto)
            .filter(Proyecto.owner_id == owner_id)
            .all()
        )

    def delete_proyecto(self, proyecto: Proyecto):
        self.db.delete(proyecto)

    def update_proyecto(
        self,
        proyecto: Proyecto,
        proyecto_data: ProyectoCreate
    ) -> Proyecto:
        proyecto.name = proyecto_data.name
        proyecto.skill = proyecto_data.skill
        proyecto.description = proyecto_data.description
        proyecto.start = proyecto_data.start
        proyecto.end = proyecto_data.end
        proyecto.image = proyecto_data.image
        proyecto.owner_id = proyecto_data.owner_id

        return proyecto

    def apply_to_project(self, proyecto_id: int, alumno_id: int) -> ProyectoAlumno:
        application = ProyectoAlumno(
            proyecto_id=proyecto_id,
            alumno_id=alumno_id,
            status="pending"
        )
        self.db.add(application)
        return application

    def get_applications_by_project(self, proyecto_id: int) -> list[ProyectoAlumno]:
        return (
            self.db.query(ProyectoAlumno)
            .filter(ProyectoAlumno.proyecto_id == proyecto_id)
            .all()
        )

    def get_application_by_id(self, application_id: int) -> ProyectoAlumno | None:
        return (
            self.db.query(ProyectoAlumno)
            .filter(ProyectoAlumno.id == application_id)
            .first()
        )

    def update_application_status(self, application: ProyectoAlumno, status: str) -> ProyectoAlumno:
        application.status = status
        return application