from fastapi import HTTPException, status
from app.db.client import get_supabase_client
from typing import List
from datetime import datetime
from app.models.session import CustomSessionResponse

class SessionController:
    @staticmethod
    async def list_sessions():
        client = get_supabase_client()
        response = client.table("sessions").select("*").execute()
        return response.data

    @staticmethod
    async def get_today_custom_session() -> CustomSessionResponse:
        client = get_supabase_client()
        today = datetime.now().strftime("%Y-%m-%d")
        response = client.table("sessions").select("*").eq("date", today).eq("is_custom_start_time", True).execute()
        
        if response.data and len(response.data) > 0:
            session_data = response.data[0]
            return CustomSessionResponse(
                hasCustomSession=True,
                checkInStartTime=session_data.get("check_in_start_time")
            )
            
        return CustomSessionResponse(hasCustomSession=False)
