from pydantic import BaseModel, Field, EmailStr, HttpUrl
from uuid import UUID

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, description="Nome completo do usuário")
    email: EmailStr = Field(..., description="Endereço de e-mail do usuário")
    profilePhotoUrl: HttpUrl = Field(..., description="URL pública da foto de perfil do usuário")

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: UUID = Field(..., description="ID único do usuário (UUID v4)")
