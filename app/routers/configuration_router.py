from fastapi import APIRouter
from typing import List
from app.models.configuration import ConfigurationResponse, ConfigurationUpdate
from app.controllers.configuration_controller import ConfigurationController

router = APIRouter(prefix="/api/v1/configurations", tags=["Configurations"])

@router.get("/", response_model=List[ConfigurationResponse], summary="Lista todas as configurações globais")
async def list_all():
    return await ConfigurationController.list_configs()

@router.get("/defaults", summary="Busca configurações de horários padrão")
async def get_defaults():
    return await ConfigurationController.get_default_times()

@router.get("/{key}", response_model=ConfigurationResponse, summary="Busca uma configuração por chave")
async def get_by_key(key: str):
    return await ConfigurationController.get_config(key)

@router.patch("/{key}", response_model=ConfigurationResponse, summary="Atualiza o valor de uma configuração")
async def update(key: str, data: ConfigurationUpdate):
    return await ConfigurationController.update_config(key, data)
