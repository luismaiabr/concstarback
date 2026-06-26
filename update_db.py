import asyncio
from app.db.client import get_supabase_client

async def main():
    client = get_supabase_client()
    
    # 1. Delete defaultstarttime
    client.table("configurations").delete().eq("key", "defaultstarttime").execute()
    print("Deleted defaultstarttime")
    
    # 2. Insert customcheckindurationdelta
    client.table("configurations").insert({
        "key": "customcheckindurationdelta",
        "value": {"timedelta": "00:10:00"},
        "description": "Duration delta for custom check-ins"
    }).execute()
    print("Inserted customcheckindurationdelta")
    
    # 3. Insert defaultcheckindurationdelta
    client.table("configurations").insert({
        "key": "defaultcheckindurationdelta",
        "value": {"timedelta": "00:10:00"},
        "description": "Duration delta for default check-ins"
    }).execute()
    print("Inserted defaultcheckindurationdelta")

if __name__ == "__main__":
    asyncio.run(main())
