from pydantic import BaseModel, Field, EmailStr, HttpUrl
from uuid import UUID

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, description="Nome completo do usuário")
    email: EmailStr = Field(..., description="Endereço de e-mail do usuário")
    profilePhotoUrl: HttpUrl | None = Field(None, description="URL pública da foto de perfil do usuário")
    profile_color: str | None = Field("#f1f5f9", description="Cor do perfil do usuário")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72, description="Senha do usuário (mínimo 8 caracteres, máximo 72)")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="E-mail de login")
    password: str = Field(..., min_length=8, max_length=72, description="Senha")

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: UUID

class TokenData(BaseModel):
    email: str | None = None

class UserResponse(UserBase):
    id: UUID = Field(..., description="ID único do usuário (UUID v4)")
