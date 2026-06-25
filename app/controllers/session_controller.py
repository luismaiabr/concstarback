from fastapi import HTTPException, status
from app.db.client import get_supabase_client
from typing import List
from datetime import datetime
from app.models.session import CustomSessionResponse, Vote

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

    @staticmethod
    async def submit_vote(vote: Vote, user_id: str):
        client = get_supabase_client()
        
        # Check if the user has already voted for this date
        existing_vote = client.table("votes").select("*").eq("date", vote.date).eq("user_id", user_id).execute()
        
        if existing_vote.data:
            existing = existing_vote.data[0]
            if existing["time"] == vote.time + ":00" or existing["time"] == vote.time:
                # If they vote for the same time, we toggle it off (delete it)
                client.table("votes").delete().eq("id", existing["id"]).execute()
                return {"status": "removed"}
            else:
                # Update existing vote to new time
                client.table("votes").update({"time": vote.time}).eq("id", existing["id"]).execute()
                return {"status": "updated"}
        else:
            # Insert new vote
            client.table("votes").insert({
                "date": vote.date,
                "time": vote.time,
                "user_id": user_id
            }).execute()
            return {"status": "added"}

    @staticmethod
    async def list_votes():
        client = get_supabase_client()
        response = client.table("votes").select("*").execute()
        return response.data
