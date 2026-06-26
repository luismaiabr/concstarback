import os
import zoneinfo
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.client import get_supabase_client
from app.models.session import CreateSessionDto
from app.controllers.session_controller import SessionController, sessionHasConflict
from fastapi import HTTPException

logger = logging.getLogger(__name__)

async def schedule_default_session():
    """
    Job that runs daily to create the default session for the day
    based on the configuration table.
    """
    logger.info("Executing daily default session job.")
    try:
        client = get_supabase_client()
        
        # 1. Fetch config from configurations
        config_response = client.table("configurations").select("*").in_("key", ["checkintime", "defaultcheckindurationdelta"]).execute()
        configs = {item["key"]: item["value"] for item in config_response.data} if config_response.data else {}
        
        check_in_time = configs.get("checkintime", "06:00:00")
        
        # Extract defaultcheckindurationdelta (might be a complex object if from timedelta)
        duration_delta = "00:10:00"
        raw_delta = configs.get("defaultcheckindurationdelta")
        if isinstance(raw_delta, dict) and "timedelta" in raw_delta:
            duration_delta = str(raw_delta["timedelta"])
        elif isinstance(raw_delta, str):
            duration_delta = raw_delta

        # 2. Get today's date
        tz_str = os.getenv("APP_TIMEZONE", "America/Sao_Paulo")
        tz = zoneinfo.ZoneInfo(tz_str)
        today = datetime.now(tz).strftime("%Y-%m-%d")

        payload = CreateSessionDto(
            date=today,
            check_in_start_time=check_in_time,
            check_in_duration_delta=duration_delta,
            is_custom_start_time=False,
            user_id="system.scheduler"
        )
        
        # 3. Check for conflicts
        try:
            await sessionHasConflict(payload)
        except HTTPException as e:
            if e.status_code == 409:
                logger.info(f"Default session already exists for {today}. Skipping creation.")
                return
            raise e
            
        # 4. Create the session
        await SessionController.create_session(payload)
        logger.info(f"Successfully created default session for {today}.")
        
    except Exception as e:
        logger.error(f"Error creating default session: {e}")

# Initialize the scheduler
scheduler = AsyncIOScheduler()

def setup_scheduler():
    """
    Configure and add jobs to the scheduler.
    """
    tz_str = os.getenv("APP_TIMEZONE", "America/Sao_Paulo")
    
    # Add job to run every day at 00:01
    scheduler.add_job(
        schedule_default_session,
        'cron',
        hour=0,
        minute=1,
        timezone=tz_str,
        id='daily_default_session'
    )

def start_scheduler():
    setup_scheduler()
    scheduler.start()
    logger.info("Scheduler started.")

def stop_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler stopped.")
