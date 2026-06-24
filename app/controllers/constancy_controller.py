from fastapi import HTTPException, status
from app.db.client import get_supabase_client
from app.models.constancy import CheckInResponse, CancelCheckInDto
from typing import List, Optional

class ConstancyController:
    @staticmethod
    async def list_days(month: Optional[str] = None):
        client = get_supabase_client()
        query = client.table("constancy_days").select("*")
        # TODO: Add month filtering if provided
        response = query.execute()
        return response.data

    @staticmethod
    async def check_in(user_id: str) -> CheckInResponse:
        client = get_supabase_client()
        insert_payload = { "user_id": user_id, "checked_in": True }
        response = client.table("check_ins").insert(insert_payload).execute()  # type: ignore
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao fazer check-in."
            )
        return CheckInResponse.model_validate(response.data[0])

    @staticmethod
    async def cancel_check_in(user_id: str, cancel_data: CancelCheckInDto) -> CheckInResponse:
        client = get_supabase_client()
        response = client.table("check_ins").update({"cancelled": True, "cancel_reason": cancel_data.reason}).eq("user_id", user_id).execute()  # type: ignore
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check-in não encontrado para cancelar.")
        return CheckInResponse.model_validate(response.data[0])
