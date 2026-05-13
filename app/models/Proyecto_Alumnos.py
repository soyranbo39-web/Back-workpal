from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class ProyectoAlumno(Base):
    __tablename__ = "ProyectoAlumno"
    __table_args__ = (UniqueConstraint('id', name='uq_proyectoalumno_id'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alumno_id: Mapped[int] = mapped_column(Integer, ForeignKey("Alumno.id"), nullable=False)
    proyecto_id: Mapped[int] = mapped_column(Integer, ForeignKey("Proyectos.id"), nullable=False)
