from datetime import datetime
from pydantic import BaseModel


class ProyectoCreate(BaseModel):
    name: str
    skill: str
    description: str
    start: datetime | None = None
    end: datetime | None = None
    image: str | None = None
    owner_id: int | None = None


class ProyectoResponse(BaseModel):
    id: int
    owner_id: int | None = None
    name: str
    skill: str
    description: str
    start: datetime
    end: datetime
    image: str | None = None

    class Config:
        from_attributes = True

class ProyectoAlumnoBase(BaseModel):
    proyecto_id: int
    alumno_id: int
    status: str = "pending"
    exit_requested: bool = False

class ProyectoAlumnoResponse(ProyectoAlumnoBase):
    id: int

    class Config:
        from_attributes = True