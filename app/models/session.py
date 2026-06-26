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
    original_checkin_time: str = Field(..., pattern=r"^\d{2}:\d{2}(:\d{2})?$", description="Horário original da sessão")

class CustomSessionResponse(BaseModel):
    hasCustomSession: bool
    checkInStartTime: str | None = None
    checkInDurationDelta: str | None = None
    sessionWorkDuration: str | None = None

class CreateSessionDto(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Data da sessão (YYYY-MM-DD)")
    check_in_start_time: str = Field(..., pattern=r"^\d{2}:\d{2}:\d{2}$", description="Horário de início (HH:MM:SS)")
    check_in_duration_delta: str = Field(..., pattern=r"^\d{2}:\d{2}:\d{2}$", description="Duração da janela de check-in (HH:MM:SS)")
    session_work_duration: str | None = Field(None, pattern=r"^\d{2}:\d{2}:\d{2}$", description="Duração do trabalho na sessão (HH:MM:SS)")
    is_custom_start_time: bool = Field(..., description="Booleano indicando se é uma sessão de usuário")
    user_id: str = Field(..., description="ID do usuário ou 'system.scheduler' para o sistema")
