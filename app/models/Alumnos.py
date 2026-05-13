
from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base


class Alumno(Base):
    __tablename__ = "Alumno"
    __table_args__ = (UniqueConstraint('id', name='uq_alumno_id'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    carrera: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    imagen_url: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    lista_proyectos: Mapped[list] = relationship(
        "Proyecto",
        secondary="ProyectoAlumno",
        back_populates="lista_alumnos"
    )
