import asyncio
from app.db.client import get_supabase_client

async def main():
    client = get_supabase_client()
    response = client.table("sessions").select("*, constancy_days(user_id, users(name, color))").execute()
    print(response.data)

if __name__ == "__main__":
    asyncio.run(main())
