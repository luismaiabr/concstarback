import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.client import get_supabase_client

def set_quota():
    client = get_supabase_client()
    
    # insert VOTE_SESSION_QUOTA
    res = client.table("configurations").upsert({
        "key": "VOTE_SESSION_QUOTA",
        "value": 2,
        "description": "Quota de votos necessarios para aprovar uma sessao"
    }).execute()
    print("Inserted VOTE_SESSION_QUOTA:", res.data)

if __name__ == "__main__":
    set_quota()
