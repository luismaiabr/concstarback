from fastapi import APIRouter
from typing import List, Optional
from app.models.constancy import CheckInResponse, CancelCheckInDto
from app.controllers.constancy_controller import ConstancyController

router = APIRouter(prefix="/api/v1/constancy", tags=["Constancy"])

@router.get("/")
async def list_days(month: Optional[str] = None):
    return await ConstancyController.list_days(month)

@router.post("/check-in", response_model=CheckInResponse)
async def check_in(user_id: str):
    return await ConstancyController.check_in(user_id)

@router.post("/cancel", response_model=CheckInResponse)
async def cancel_check_in(user_id: str, cancel_data: CancelCheckInDto):
    return await ConstancyController.cancel_check_in(user_id, cancel_data)
