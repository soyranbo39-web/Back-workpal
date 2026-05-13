from datetime import datetime
from pydantic import BaseModel


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