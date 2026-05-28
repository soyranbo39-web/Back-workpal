from datetime import datetime
from pydantic import BaseModel

class TareaCreate(BaseModel):
    title: str
    description: str
    end_date: datetime
    assigned_to: int

class TareaUpdateStatus(BaseModel):
    status: str

class TareaResponse(BaseModel):
    id: int
    proyecto_id: int
    assigned_to: int
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    status: str
    responsable_name: str | None = None

    class Config:
        from_attributes = True
