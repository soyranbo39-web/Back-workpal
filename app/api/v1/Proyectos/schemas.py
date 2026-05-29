from datetime import datetime
from pydantic import BaseModel
from fastapi import Form


class ProyectoCreate(BaseModel):
    name: str
    skill: str
    description: str
    start: datetime | None = None
    end: datetime | None = None
    image: str | None = None
    owner_id: int | None = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        skill: str = Form(...),
        description: str = Form(...),
        start: datetime | None = Form(None),
        end: datetime | None = Form(None),
        owner_id: int | None = Form(None)
    ):
        return cls(
            name=name,
            skill=skill,
            description=description,
            start=start,
            end=end,
            owner_id=owner_id
        )


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