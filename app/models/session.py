from pydantic import BaseModel, Field
from uuid import UUID

class Session(BaseModel):
    id: UUID = Field(..., description="ID único do registro de sessão (UUID v4)")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Data da sessão")
    checkInStartTime: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Horário de início/sugerido")
    isCustomStartTime: bool = Field(..., description="Se for false, é o horário padrão. Se true, é um voto de customização.")
    user: str = Field(..., description="Identificador do usuário que propôs/votou, ou 'system' para o padrão.")

class Vote(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Data da sessão na qual o voto foi registrado")
    time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Horário sugerido pelo voto")
    userId: str = Field(..., description="ID único do usuário que registrou o voto")
