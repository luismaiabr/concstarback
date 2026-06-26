import asyncio
from app.core.scheduler import schedule_default_session

async def main():
    await schedule_default_session()
    print("Done")

if __name__ == "__main__":
    asyncio.run(main())
