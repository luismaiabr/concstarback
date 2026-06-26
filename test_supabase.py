from app.db.client import get_supabase_client
import sys

client = get_supabase_client()
res = client.table("check_ins").select("*").limit(1).execute()
print(res.data)
