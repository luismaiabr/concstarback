import asyncio
from app.db.client import get_supabase_client
from app.models.session import Vote
from app.controllers.session_controller import SessionController

async def test():
    vote = Vote(
        date="2026-06-25",
        time="00:00",
        original_checkin_time="00:00"
    )
    res = await SessionController.submit_vote(vote, "dc891eb0-0e8b-4161-a583-4d5075f78fd7")
    print("Result:", res)

if __name__ == "__main__":
    asyncio.run(test())
