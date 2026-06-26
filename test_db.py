import asyncio
from app.db.client import get_supabase_client

async def main():
    client = get_supabase_client()
    try:
        # Unfortunately, Supabase JS/Py clients don't let you query information_schema easily
        # but let's try an insert with only date, or just try to get the error details
        resp = client.table("sessions").insert({"date": "2026-06-26"}).execute()
        print(resp.data)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
