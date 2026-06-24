from pydantic import BaseModel, Field
from typing import Any, Optional, Union, List
from enum import Enum
from datetime import datetime

class SettingType(str, Enum):
    TIME = "TIME"
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    OPTIONS = "OPTIONS"

class GeneralSetting(BaseModel):
    name: str = Field(..., description="O nome do setting")
    type: SettingType = Field(..., description="O tipo do setting")
    selectedConfiguration: Optional[Union[str, int, bool]] = Field(None, description="A configuração escolhida pelo usuário")
    enums: Optional[List[Union[str, int]]] = Field(None, description="Lista de opções disponíveis")
    value: Optional[Any] = Field(None, description="Valores complementares")

class ConfigurationBase(BaseModel):
    key: str = Field(..., description="Chave identificadora única", json_schema_extra={"example": "MIN_WORD_REGISTER_QUESTIONS"})
    value: Any = Field(..., description="Valor da configuração (qualquer formato JSON)", json_schema_extra={"example": 5})
    description: Optional[str] = Field(None, description="Descrição da funcionalidade do parâmetro")

class ConfigurationCreate(ConfigurationBase):
    pass

class ConfigurationUpdate(BaseModel):
    value: Any = Field(..., description="Novo valor a ser salvo")
    description: Optional[str] = Field(None, description="Descrição atualizada")

class ConfigurationResponse(ConfigurationBase):
    created_at: datetime
    updated_at: datetime
