from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Proyectos import Proyecto
    from .Alumnos import Alumno

class Tarea(Base):
    __tablename__ = "Tareas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    proyecto_id: Mapped[int] = mapped_column(Integer, ForeignKey("Proyectos.id"), nullable=False)
    assigned_to: Mapped[int] = mapped_column(Integer, ForeignKey("Alumno.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Pendiente") # Pendiente, En Proceso, Completada, Confirmada

    proyecto: Mapped["Proyecto"] = relationship("Proyecto", back_populates="tareas")
    responsable: Mapped["Alumno"] = relationship("Alumno")
