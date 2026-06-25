from fastapi import APIRouter
from app.controllers.session_controller import SessionController

router = APIRouter(prefix="/api/v1/sessions", tags=["Sessions"])

@router.get("/today")
async def get_today_custom_session():
    return await SessionController.get_today_custom_session()

@router.get("/")
async def list_sessions():
    return await SessionController.list_sessions()
