# 03 - Contratos da API e Controladores

## 1. Mapeamento de Rotas (View Layer - `routers/`)

O FastAPI exporá endpoints sob o prefixo `/api/v1/`. As rotas servem apenas para roteamento e validação de schema. Toda a carga de processamento será repassada aos Controllers.

### Entidade: Users (`/api/v1/users`)
| Método | Endpoint | Controller.Metodo | Payload Entrada (Pydantic) | Payload Saída (Pydantic) |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | `UserController.list_users` | - | `List[UserResponse]` |
| `POST` | `/` | `UserController.create_user` | `UserCreateRequest` | `UserResponse` |
| `GET` | `/{user_id}`| `UserController.get_user` | - | `UserResponse` |
| `PATCH`| `/{user_id}`| `UserController.update_user` | `UserUpdateRequest` | `UserResponse` |

### Entidade: Auth (`/api/v1/auth`)
| Método | Endpoint | Controller.Metodo | Payload Entrada | Payload Saída |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/register` | `AuthController.register` | `UserRegisterRequest` | `UserResponse` |

### Entidade: Constancy (`/api/v1/constancy`)
| Método | Endpoint | Controller.Metodo | Payload Entrada | Payload Saída |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | `ConstancyController.list_days` | `?month=...` (Query) | `List[ConstancyDayResponse]` |
| `POST` | `/check-in` | `ConstancyController.check_in` | - | `CheckInResponse`|
| `POST` | `/cancel` | `ConstancyController.cancel_check_in` | `CancelCheckInDto` | `CheckInResponse`|

### Entidade: Questions (`/api/v1/questions`)
| Método | Endpoint | Controller.Metodo | Payload Entrada | Payload Saída |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | `QuestionController.list_questions` | - | `List[QuestionResponse]` |
| `POST` | `/` | `QuestionController.create_question` | `CreateQuestionDto` | `QuestionResponse` |

### Entidade: Configurations (`/api/v1/configurations`)
| Método | Endpoint | Controller.Metodo | Payload Entrada | Payload Saída |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | `ConfigurationController.list_configs` | - | `List[ConfigurationResponse]` |
| `GET` | `/{key}`| `ConfigurationController.get_config` | - | `ConfigurationResponse` |
| `PATCH`| `/{key}`| `ConfigurationController.update_config` | `ConfigurationUpdateRequest` | `ConfigurationResponse` |

## 2. Contratos Pydantic (Model Layer - `models/`)

Exemplos de contratos essenciais seguindo rigor técnico:

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

# --- USERS ---
class UserCreateRequest(BaseModel):
    email: EmailStr = Field(..., description="E-mail único do usuário", example="user@example.com")
    name: str = Field(..., min_length=2, max_length=150, description="Nome completo")
    color: str = Field(default="#000000", description="Cor de perfil do usuário")
    isActive: Optional[bool] = Field(default=True, description="Flag de controle de ativação")

class UserResponse(UserCreateRequest):
    id: UUID = Field(..., description="Identificador único")
    created_at: datetime
    updated_at: datetime

class UserRegisterRequest(UserCreateRequest):
    password: str = Field(..., min_length=8, description="Senha do usuário")

# --- CONSTANCY ---
class CancelCheckInDto(BaseModel):
    reason: str = Field(..., description="Motivo do cancelamento")

class UserConstancyResponse(BaseModel):
    checkedIn: bool
    cumulativeY: int

class ConstancyDayResponse(BaseModel):
    id: UUID
    date: str
    users: Dict[str, UserConstancyResponse]

class CheckInResponse(BaseModel):
    id: UUID
    constancy_day_id: UUID
    user_id: UUID
    checked_in: bool
    cumulative_y: int

# --- QUESTIONS ---
class CreateQuestionDto(BaseModel):
    amount: float = Field(..., description="Quantidade ou valor")
    description: str = Field(..., description="Descrição da pergunta")

class QuestionResponse(CreateQuestionDto):
    id: int
    user: str = Field(..., description="Nome ou ID do usuário criador")
    date: datetime

# --- CONFIGURATIONS ---
class ConfigurationUpdateRequest(BaseModel):
    value: Any = Field(..., description="Novo valor a ser salvo (formato JSONb compatível)")
    description: Optional[str] = Field(None, description="Descrição atualizada da configuração")

class ConfigurationResponse(BaseModel):
    key: str = Field(..., description="Identificador único da configuração")
    value: Any = Field(..., description="Valor da configuração")
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
```

## 3. Padrão de Comunicação com o Supabase (Controller Layer - `controllers/`)

A camada Controller assume a responsabilidade de orquestração assíncrona. Exemplo de estrutura padrão:

# controllers/constancy_controller.py
from fastapi import HTTPException, status
from app.db.supabase import get_db_client
from app.models.constancy import CancelCheckInDto, CheckInResponse

class ConstancyController:
    @staticmethod
    async def check_in(user_id: str) -> CheckInResponse:
        client = get_db_client()
        
        # 1. Obter dia atual
        # 2. Registrar Check-in (Chamada ao Supabase)
        insert_payload = { "user_id": user_id, "checked_in": True }
        response = client.table("check_ins").insert(insert_payload).execute()
        
        # 3. Tratamento e Validação de Retorno
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao fazer check-in."
            )
            
        # 4. Retorno Serializado
        return CheckInResponse(**response.data[0])
```
