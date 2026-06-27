from fastapi import HTTPException, status
from app.db.client import get_supabase_client
from typing import List
from datetime import datetime
from app.models.session import CustomSessionResponse, Vote, CreateSessionDto, CheckoutSessionDto

async def sessionHasConflict(payload: CreateSessionDto):
    if payload.is_custom_start_time:
        return False # Allow multiple custom sessions per day

    client = get_supabase_client()
    response = client.table("sessions").select("id").eq("date", payload.date).eq("is_custom_start_time", False).execute()
    if response.data and len(response.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Default session already exists for this date."
        )
    return False

class SessionController:
    @staticmethod
    async def create_session(payload: CreateSessionDto):
        client = get_supabase_client()
        
        session_work_duration = payload.session_work_duration
        if not session_work_duration:
            config_response = client.table("configurations").select("value").eq("key", "default_session_work_duration").execute()
            session_work_duration = "00:50:00"
            if config_response.data and len(config_response.data) > 0:
                item = config_response.data[0]
                if isinstance(item, dict):
                    val = item.get("value")
                    if isinstance(val, dict):
                        session_work_duration = str(val.get("timedelta", "00:50:00"))

        data = {
            "date": payload.date,
            "check_in_start_time": payload.check_in_start_time,
            "check_in_duration_delta": payload.check_in_duration_delta,
            "session_work_duration": session_work_duration,
            "is_custom_start_time": payload.is_custom_start_time,
            "user_id": payload.user_id
        }
        # In Supabase, if we insert, it will return the inserted row
        response = client.table("sessions").insert(data).execute()
        return response.data

    @staticmethod
    async def list_sessions():
        client = get_supabase_client()
        response = client.table("sessions").select("*, constancy_days(user_id, users(name, profile_color))").execute()
        
        sessions = response.data
        import os
        import zoneinfo
        from datetime import datetime, timedelta
        
        tz_str = os.getenv("APP_TIMEZONE", "America/Sao_Paulo")
        tz = zoneinfo.ZoneInfo(tz_str)
        now = datetime.now(tz)
        
        result = []
        for session in sessions:
            session_date_str = session.get("date")
            check_in_start_str = session.get("check_in_start_time", "00:00:00")
            duration_delta_str = session.get("check_in_duration_delta", "00:10:00")
            work_duration_str = session.get("session_work_duration", "00:50:00")
            
            def parse_time_str(t_str):
                parts = t_str.split(":")
                h = int(parts[0]) if len(parts) > 0 else 0
                m = int(parts[1]) if len(parts) > 1 else 0
                s = int(parts[2]) if len(parts) > 2 else 0
                return timedelta(hours=h, minutes=m, seconds=s)
            
            try:
                dt_str = f"{session_date_str} {check_in_start_str}"
                session_start_time = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
                delta_td = parse_time_str(duration_delta_str)
                work_td = parse_time_str(work_duration_str)
                session_end_time = session_start_time + delta_td + work_td
                is_finished = now >= session_end_time
            except Exception:
                is_finished = False

            checkouts_realizados = []
            constancy_records = session.get("constancy_days") or []
            # Sometimes constancy_days could be a dict if returning single item, but usually list
            if isinstance(constancy_records, dict):
                constancy_records = [constancy_records]
                
            for record in constancy_records:
                user_info = record.get("users") or {}
                # PostgREST can return nested lists if it's 1-to-many, but users is many-to-1 from constancy_days
                if isinstance(user_info, list) and len(user_info) > 0:
                    user_info = user_info[0]
                elif isinstance(user_info, list):
                    user_info = {}
                    
                checkouts_realizados.append({
                    "user_id": record.get("user_id"),
                    "name": user_info.get("name", "Unknown"),
                    "color": user_info.get("profile_color") or "#f1f5f9"
                })
                
            session_dict = session.copy()
            session_dict.pop("constancy_days", None)
            session_dict["is_finished"] = is_finished
            session_dict["checkouts_realizados"] = checkouts_realizados
            
            result.append(session_dict)
            
        return result

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
                        
            # Fetch custom session work duration
            work_dur_response = client.table("sessions").select("session_work_duration").eq("date", today).eq("is_custom_start_time", True).execute()
            session_work_duration = "00:50:00"
            if work_dur_response.data and len(work_dur_response.data) > 0:
                session_work_duration = work_dur_response.data[0].get("session_work_duration", "00:50:00")
                
            return CustomSessionResponse(
                hasCustomSession=True,
                checkInStartTime=f"{top_time}:00",
                checkInDurationDelta=duration_delta,
                sessionWorkDuration=session_work_duration
            )
            
        return CustomSessionResponse(hasCustomSession=False)

    @staticmethod
    async def submit_vote(vote: Vote, user_id: str):
        client = get_supabase_client()
        
        # Check if the user has already voted for this date and specific session
        existing_vote = client.table("votes").select("*").eq("date", vote.date).eq("original_checkin_time", vote.original_checkin_time).eq("user_id", user_id).execute()
        
        status_msg = "added"
        if existing_vote.data:
            existing = existing_vote.data[0]
            if existing["time"] == vote.time + ":00" or existing["time"] == vote.time:
                # If they vote for the same time, we toggle it off (delete it)
                client.table("votes").delete().eq("id", existing["id"]).execute()
                return {"status": "removed"}
            else:
                # Update existing vote to new time
                client.table("votes").update({"time": vote.time}).eq("id", existing["id"]).execute()
                status_msg = "updated"
        else:
            # Insert new vote
            client.table("votes").insert({
                "date": vote.date,
                "time": vote.time,
                "original_checkin_time": vote.original_checkin_time,
                "user_id": user_id
            }).execute()

        # Check if this vote reached the quota
        all_votes = client.table("votes").select("*").eq("date", vote.date).eq("original_checkin_time", vote.original_checkin_time).eq("time", vote.time).execute()
        
        quota = 1
        config_response = client.table("configurations").select("value").eq("key", "VOTE_SESSION_QUOTA").execute()
        if config_response.data:
            try:
                quota = int(config_response.data[0].get("value", 1))
            except ValueError:
                pass
                
        if len(all_votes.data) == quota:
            # Fetch old session to get configs, or use defaults
            old_session = client.table("sessions").select("*").eq("date", vote.date).eq("check_in_start_time", vote.original_checkin_time + ":00").execute()
            
            duration_delta = "00:10:00"
            work_duration = "00:50:00"
            
            if old_session.data:
                duration_delta = old_session.data[0].get("check_in_duration_delta", duration_delta)
                work_duration = old_session.data[0].get("session_work_duration", work_duration)
                client.table("sessions").delete().eq("id", old_session.data[0]["id"]).execute()
            
            # Insert new session if it doesn't already exist
            new_session_data = {
                "date": vote.date,
                "check_in_start_time": vote.time + ":00",
                "check_in_duration_delta": duration_delta,
                "session_work_duration": work_duration,
                "is_custom_start_time": True,
                "user_id": user_id
            }
            existing_target = client.table("sessions").select("id").eq("date", vote.date).eq("check_in_start_time", vote.time + ":00").execute()
            if not existing_target.data:
                client.table("sessions").insert(new_session_data).execute()
            
            # Note: We NO LONGER delete the votes here so that the UI can show the historical consensus.
            
            status_msg = "adopted"

        return {"status": status_msg}

    @staticmethod
    async def list_votes():
        client = get_supabase_client()
        response = client.table("votes").select("*").execute()
        return response.data

    @staticmethod
    async def checkout_session(payload: CheckoutSessionDto, user_id: str):
        client = get_supabase_client()
        
        # Check if already exists to avoid throwing unique constraint error directly to client
        # though we could also just let Supabase handle it if we want.
        existing = client.table("constancy_days") \
            .select("id") \
            .eq("date", payload.date) \
            .eq("user_id", user_id) \
            .eq("session_id", str(payload.session_id)) \
            .execute()
            
        if existing.data and len(existing.data) > 0:
            return {"status": "already_checked_out"}
            
        # Insert checkout record
        try:
            client.table("constancy_days").insert({
                "date": payload.date,
                "user_id": user_id,
                "session_id": str(payload.session_id)
            }).execute()
        except Exception as e:
            # Handle potential duplicate key race condition
            if "duplicate key value violates unique constraint" in str(e):
                return {"status": "already_checked_out"}
            raise HTTPException(status_code=500, detail=str(e))
            
        return {"status": "success"}
