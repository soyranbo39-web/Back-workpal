from sqlalchemy import Integer, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base


class ProyectoAlumno(Base):
    __tablename__ = "ProyectoAlumno"
    __table_args__ = (
        UniqueConstraint('alumno_id', 'proyecto_id', name='uq_alumno_proyecto'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    proyecto_id: Mapped[int] = mapped_column(Integer, ForeignKey("Proyectos.id"), nullable=False)
    alumno_id: Mapped[int] = mapped_column(Integer, ForeignKey("Alumno.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending") # pending, accepted, rejected