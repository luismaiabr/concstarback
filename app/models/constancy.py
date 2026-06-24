from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class Cancellation(BaseModel):
    userId: str = Field(..., description="ID único do usuário que cancelou a sessão")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Data da sessão cancelada")
    reason: str = Field(..., min_length=1, description="Motivo que justifica o cancelamento da sessão")

class CancelCheckInDto(BaseModel):
    reason: str = Field(..., description="Motivo do cancelamento")

class CheckInResponse(BaseModel):
    id: UUID
    constancy_day_id: UUID
    user_id: UUID
    checked_in: bool
    cumulative_y: int
    cancelled: bool
    cancel_reason: Optional[str] = None
