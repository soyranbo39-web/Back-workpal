from sqlalchemy.orm import Session

from app.api.v1.Alumnos.schemas import AlumnoCreate
from app.models.Alumnos import Alumno


class AlumnoRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_alumno(self, alumno: AlumnoCreate, user_id: str | None = None) -> Alumno:
        new_alumno = Alumno(
            name=alumno.name,
            last_name=alumno.last_name,
            carrera=alumno.carrera,
            skills=alumno.skills,
            imagen_url=getattr(alumno, "imagen_url", ""),
            user_id=user_id
        )
        self.db.add(new_alumno)
        return new_alumno

    def get_alumno_by_id(self, alumno_id: int) -> Alumno | None:
        return (
            self.db.query(Alumno)
            .filter(Alumno.id == alumno_id)
            .first()
        )

    def get_alumno_by_user_id(self, user_id: str) -> Alumno | None:
        return (
            self.db.query(Alumno)
            .filter(Alumno.user_id == user_id)
            .first()
        )

    def list_alumnos(self) -> list[Alumno]:
        return self.db.query(Alumno).all()

    def delete_alumno(self, alumno: Alumno):
        self.db.delete(alumno)

    def update_alumno(
        self,
        alumno: Alumno,
        alumno_data: AlumnoCreate
    ) -> Alumno:
        alumno.name = alumno_data.name
        alumno.last_name = alumno_data.last_name
        alumno.carrera = alumno_data.carrera
        alumno.skills = alumno_data.skills
        alumno.imagen_url = alumno_data.imagen_url

        return alumno