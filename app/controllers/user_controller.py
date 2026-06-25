from fastapi import HTTPException, status
from app.db.client import get_supabase_client
from app.models.user import UserCreate, UserResponse
from typing import List
from uuid import UUID

class UserController:
    @staticmethod
    async def list_users() -> List[UserResponse]:
        client = get_supabase_client()
        response = client.table("users").select("*").execute()
        return [UserResponse.model_validate(item) for item in response.data]

    @staticmethod
    async def create_user(user: UserCreate) -> UserResponse:
        client = get_supabase_client()
        
        # Check if email already exists
        existing = client.table("users").select("id").eq("email", user.email).execute()
        if existing.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")
            
        from app.core.security import get_password_hash
        
        user_data = user.model_dump(mode="json")
        password = user_data.pop("password")
        user_data.pop("profilePhotoUrl", None)
        user_data["hashed_password"] = get_password_hash(password)
        
        response = client.table("users").insert(user_data).execute()  # type: ignore
        if not response.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao criar usuário")
        return UserResponse.model_validate(response.data[0])

    @staticmethod
    async def get_user(user_id: UUID) -> UserResponse:
        client = get_supabase_client()
        response = client.table("users").select("*").eq("id", str(user_id)).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        return UserResponse.model_validate(response.data[0])
