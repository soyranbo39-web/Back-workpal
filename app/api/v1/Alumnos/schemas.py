from datetime import datetime
from typing import Annotated

from fastapi import Form
from pydantic import BaseModel


class AlumnoCreate(BaseModel):
    name: str
    last_name: str
    carrera: str
    imagen_url: str = ""

    @classmethod
    def as_form(
        cls,
        name: Annotated[str, Form()],
        last_name: Annotated[str, Form()],
        carrera: Annotated[str, Form()],
    ) -> "AlumnoCreate":
        return cls(name=name, last_name=last_name, carrera=carrera)

class AlumnoResponse(BaseModel):
    id: int
    name: str
    last_name: str
    carrera: str
    imagen_url: str = ""

    class Config:
        from_attributes = True


class ProyectoCreate(BaseModel):
    name: str
    skill: str
    description: str
    start: datetime | None = None
    end: datetime | None = None
    image: str | None = None


class ProyectoResponse(BaseModel):
    id: int
    name: str
    skill: str
    description: str
    start: datetime
    end: datetime
    image: str | None = None

    class Config:
        from_attributes = True