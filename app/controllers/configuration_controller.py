from fastapi import HTTPException, status
from app.db.client import get_supabase_client
from app.models.configuration import ConfigurationResponse, ConfigurationUpdate
from typing import List

class ConfigurationController:
    @staticmethod
    async def get_config(key: str) -> ConfigurationResponse:
        client = get_supabase_client()
        response = client.table("configurations").select("*").eq("key", key).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuração '{key}' não localizada no banco de dados."
            )
            
        return ConfigurationResponse.model_validate(response.data[0])

    @staticmethod
    async def list_configs() -> List[ConfigurationResponse]:
        client = get_supabase_client()
        response = client.table("configurations").select("*").execute()
        return [ConfigurationResponse.model_validate(item) for item in response.data]

    @staticmethod
    async def update_config(key: str, data: ConfigurationUpdate) -> ConfigurationResponse:
        client = get_supabase_client()
        update_payload = data.model_dump(exclude_unset=True)
        
        response = client.table("configurations").update(update_payload).eq("key", key).execute()  # type: ignore
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Falha ao atualizar configuração '{key}'."
            )
            
        return ConfigurationResponse.model_validate(response.data[0])
