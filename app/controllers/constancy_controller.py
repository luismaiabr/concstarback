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
        from datetime import datetime
        from app.controllers.session_controller import SessionController
        import os
        import zoneinfo
        from app.controllers.configuration_controller import ConfigurationController
        
        # Fetch default times dynamically
        default_times = await ConfigurationController.get_default_times()
        checkin_time_str = default_times.get("checkintime", "06:00:00")
        duration_delta_str = default_times.get("defaultcheckindurationdelta", "00:10:00")

        # Try fetching custom session
        custom_session = await SessionController.get_today_custom_session()
        if custom_session.hasCustomSession:
            if custom_session.checkInStartTime:
                checkin_time_str = custom_session.checkInStartTime
            if custom_session.checkInDurationDelta:
                duration_delta_str = custom_session.checkInDurationDelta
            elif "customcheckindurationdelta" in default_times:
                duration_delta_str = default_times["customcheckindurationdelta"]

        tz_str = os.getenv("APP_TIMEZONE", "America/Sao_Paulo")
        tz = zoneinfo.ZoneInfo(tz_str)
        now = datetime.now(tz)
        # parse hours, mins, secs
        def parse_time(t_str):
            parts = t_str.split(":")
            h = int(parts[0]) if len(parts) > 0 else 0
            m = int(parts[1]) if len(parts) > 1 else 0
            s = int(parts[2]) if len(parts) > 2 else 0
            return now.replace(hour=h, minute=m, second=s, microsecond=0)

        def parse_timedelta(t_str):
            from datetime import timedelta
            parts = t_str.split(":")
            h = int(parts[0]) if len(parts) > 0 else 0
            m = int(parts[1]) if len(parts) > 1 else 0
            s = int(parts[2]) if len(parts) > 2 else 0
            return timedelta(hours=h, minutes=m, seconds=s)

        try:
            checkin_time = parse_time(checkin_time_str)
            duration_delta = parse_timedelta(duration_delta_str)
            start_time = checkin_time + duration_delta

            # if now < checkin_time or now >= start_time:
            #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Fora do horário de check-in permitido.")
        except ValueError:
            pass # ignore parse errors

        client = get_supabase_client()
        date_str = now.strftime("%Y-%m-%d")
        
        # Ensure a constancy_day exists for today
        constancy_day_response = client.table("constancy_days").select("id").eq("date", date_str).execute()
        if constancy_day_response.data and len(constancy_day_response.data) > 0:
            constancy_day_id = constancy_day_response.data[0]["id"]
        else:
            new_day = client.table("constancy_days").insert({"date": date_str}).execute()
            if not new_day.data:
                raise HTTPException(status_code=500, detail="Falha ao criar constancy day.")
            constancy_day_id = new_day.data[0]["id"]

        insert_payload = { 
            "constancy_day_id": constancy_day_id,
            "user_id": user_id, 
            "checked_in": True, 
            "created_at": checkin_time.isoformat() 
        }
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

    @staticmethod
    async def get_user_constancy(user_id: str) -> dict:
        client = get_supabase_client()
        
        # 1. Fetch check-ins
        checkins_response = client.table("check_ins").select("created_at").eq("user_id", user_id).eq("checked_in", True).execute()
        
        # 2. Fetch questions to count total work
        questions_response = client.table("questions").select("amount, date").eq("user_id", user_id).execute()
        
        dates_set = set()
        total_work = 0
        
        for record in checkins_response.data:
            if "created_at" in record and record["created_at"]:
                date_str = record["created_at"][:10]
                dates_set.add(date_str)
            total_work += 1
            
        for record in questions_response.data:
            amount = float(record.get("amount", 0))
            total_work += int(amount)
            
            date_val = record.get("date")
            
            if date_val:
                dates_set.add(date_val[:10])
                
        return {
            "user_id": user_id,
            "dates": sorted(list(dates_set)),
            "total_work": total_work
        }
