from sqlalchemy.orm import Session

from app.api.v1.Alumnos.schemas import AlumnoCreate, AlumnoResponse
from app.models.Alumnos import Alumno


class PostRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_alumno(self, alumno: AlumnoCreate) -> Alumno:
        new_alumno = Alumno(
            name=alumno.name,
            last_name=alumno.last_name,
            carrera=alumno.carrera,
            imagen_url=getattr(alumno, "imagen_url", ""),
        )
        self.db.add(new_alumno)
        return new_alumno
