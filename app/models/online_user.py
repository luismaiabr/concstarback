from pydantic import BaseModel, Field, HttpUrl

class OnlineUser(BaseModel):
    name: str = Field(..., min_length=1, description="Nome do usuário online na sessão")
    profileUrl: HttpUrl = Field(..., description="URL do perfil do usuário online")
