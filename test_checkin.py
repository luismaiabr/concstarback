import asyncio
from app.db.client import get_supabase_client
from datetime import datetime
import zoneinfo

async def main():
    client = get_supabase_client()
    tz = zoneinfo.ZoneInfo("America/Sao_Paulo")
    now = datetime.now(tz)
    user_id = "dc891eb0-0e8b-4161-a583-4d5075f78fd7"
    insert_payload = { "user_id": user_id, "checked_in": True, "created_at": now.isoformat() }
    print("Payload:", insert_payload)
    try:
        response = client.table("check_ins").insert(insert_payload).execute()
        print(response)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
