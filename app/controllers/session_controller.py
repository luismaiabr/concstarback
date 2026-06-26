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
        import os
        import zoneinfo
        tz_str = os.getenv("APP_TIMEZONE", "America/Sao_Paulo")
        tz = zoneinfo.ZoneInfo(tz_str)
        today = datetime.now(tz).strftime("%Y-%m-%d")
        
        # Obter todos os votos de hoje
        votes_response = client.table("votes").select("*").eq("date", today).execute()
        votes_data = votes_response.data
        
        if not votes_data:
            return CustomSessionResponse(hasCustomSession=False)
            
        # Contar os votos por horário
        vote_counts = {}
        for vote in votes_data:
            # O horário pode vir como '10:00:00', extrair apenas HH:MM
            time_str = vote["time"][:5]
            vote_counts[time_str] = vote_counts.get(time_str, 0) + 1
            
        # Encontrar o horário com mais votos
        if not vote_counts:
            return CustomSessionResponse(hasCustomSession=False)
            
        top_time = max(vote_counts, key=vote_counts.get)
        top_votes = vote_counts[top_time]
        
        # Buscar a quota de votos (padrão 1 se não existir)
        quota = 1
        config_response = client.table("configurations").select("value").eq("key", "VOTE_SESSION_QUOTA").execute()
        if config_response.data:
            try:
                quota = int(config_response.data[0].get("value", 1))
            except ValueError:
                pass
                
        if top_votes >= quota:
            # top_time is HH:MM
            
            # Fetch custom checkin duration delta
            delta_response = client.table("configurations").select("value").eq("key", "customcheckindurationdelta").execute()
            duration_delta = "00:10:00"
            if delta_response.data and isinstance(delta_response.data, list) and len(delta_response.data) > 0:
                item = delta_response.data[0]
                if isinstance(item, dict):
                    val = item.get("value")
                    if isinstance(val, dict):
                        duration_delta = str(val.get("timedelta", "00:10:00"))
                
            return CustomSessionResponse(
                hasCustomSession=True,
                checkInStartTime=f"{top_time}:00",
                checkInDurationDelta=duration_delta
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
