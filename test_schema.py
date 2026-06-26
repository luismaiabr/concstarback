import asyncio
from app.db.client import get_supabase_client
async def main():
    client = get_supabase_client()
    resp = client.table("sessions").select("*").limit(1).execute()
    print(resp.data)
asyncio.run(main())
