from fastapi import HTTPException, status
from app.db.client import get_supabase_client
from typing import List

class SessionController:
    @staticmethod
    async def list_sessions():
        client = get_supabase_client()
        response = client.table("sessions").select("*").execute()
        return response.data
