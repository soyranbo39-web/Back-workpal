from sqlalchemy.orm import Session

from app.api.v1.Proyectos.schemas import ProyectoCreate
from app.models.Proyectos import Proyecto


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

        return proyecto