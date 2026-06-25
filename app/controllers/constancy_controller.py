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

        # Determinar checkin_time e start_time
        checkin_time_str = "06:00:00"
        start_time_str = "06:10:00"

        # Try reading .config
        config_path = os.path.join(os.path.dirname(__file__), "../../../frontend/public/.config")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                for line in f:
                    parts = line.strip().split("=")
                    if len(parts) == 2:
                        if parts[0].strip() == "CHECKIN_START_TIME":
                            checkin_time_str = parts[1].strip()
                        elif parts[0].strip() == "STARTTIME":
                            start_time_str = parts[1].strip()

        # Try fetching custom session
        custom_session = await SessionController.get_today_custom_session()
        if custom_session.hasCustomSession:
            if custom_session.checkInStartTime:
                checkin_time_str = custom_session.checkInStartTime
            if custom_session.startTime:
                start_time_str = custom_session.startTime

        now = datetime.now()
        # parse hours, mins, secs
        def parse_time(t_str):
            parts = t_str.split(":")
            h = int(parts[0]) if len(parts) > 0 else 0
            m = int(parts[1]) if len(parts) > 1 else 0
            s = int(parts[2]) if len(parts) > 2 else 0
            return now.replace(hour=h, minute=m, second=s, microsecond=0)

        try:
            checkin_time = parse_time(checkin_time_str)
            start_time = parse_time(start_time_str)

            if now < checkin_time or now >= start_time:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Fora do horário de check-in permitido.")
        except ValueError:
            pass # ignore parse errors

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
