from fastapi import APIRouter
from typing import List
from uuid import UUID
from app.models.user import UserCreate, UserResponse
from app.controllers.user_controller import UserController

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
async def list_users():
    return await UserController.list_users()

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    return await UserController.create_user(user)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID):
    return await UserController.get_user(user_id)

@router.get("/{user_id}/color")
async def get_user_color(user_id: UUID):
    return await UserController.get_user_color(user_id)
