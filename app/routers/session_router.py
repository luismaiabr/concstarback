from fastapi import APIRouter, Depends
from app.controllers.session_controller import SessionController, sessionHasConflict
from app.core.security import get_current_user
from app.models.session import Vote, CreateSessionDto

router = APIRouter(prefix="/api/v1/sessions", tags=["Sessions"])

@router.post("/")
async def create_session(payload: CreateSessionDto, conflict_check: bool = Depends(sessionHasConflict)):
    return await SessionController.create_session(payload)

@router.get("/today")
async def get_today_custom_session():
    return await SessionController.get_today_custom_session()

@router.get("/")
async def list_sessions():
    return await SessionController.list_sessions()

@router.post("/vote")
async def submit_vote(vote: Vote, user_id: str = Depends(get_current_user)):
    return await SessionController.submit_vote(vote, user_id)

@router.get("/votes")
async def list_votes():
    return await SessionController.list_votes()
