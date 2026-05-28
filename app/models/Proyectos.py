from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base


class Proyecto(Base):
    __tablename__ = "Proyectos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("Alumno.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    skill: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    start: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True)

    owner: Mapped["Alumno"] = relationship("Alumno", foreign_keys=[owner_id])
    lista_alumnos: Mapped[list["Alumno"]] = relationship(
        "Alumno",
        secondary="ProyectoAlumno",
        back_populates="lista_proyectos"
    )
    tareas: Mapped[list["Tarea"]] = relationship("Tarea", back_populates="proyecto")