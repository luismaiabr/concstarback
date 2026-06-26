import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.client import get_supabase_client

def seed_configs():
    client = get_supabase_client()
    
    # insert defaultcheckintime
    res1 = client.table("configurations").upsert({
        "key": "defaultcheckintime",
        "value": {"time": "06:00:00"},
        "description": "Horario padrão de checkin"
    }).execute()
    print("Inserted defaultcheckintime:", res1.data)

    # insert defaultstarttime
    res2 = client.table("configurations").upsert({
        "key": "defaultstarttime",
        "value": {"time": "06:10:00"},
        "description": "Horario padrão de inicio"
    }).execute()
    print("Inserted defaultstarttime:", res2.data)

if __name__ == "__main__":
    seed_configs()
