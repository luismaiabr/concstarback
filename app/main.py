import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.exceptions import global_exception_handler, business_exception_handler, CustomBusinessException
from app.core.scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup (disable scheduler on Vercel's serverless environment)
    if not os.getenv("VERCEL"):
        start_scheduler()
    yield
    # Shutdown
    if not os.getenv("VERCEL"):
        stop_scheduler()

app = FastAPI(
    title="Concstar Backend",
    description="Backend API for Concstar",
    version="0.1.0",
    lifespan=lifespan
)

from app.core.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://100.101.78.95:4203",
        "http://100.101.78.95:4203/",
        "https://concstarfront.vercel.app",
        "https://concstarfront.vercel.app/",
        "http://concstarfront.vercel.app",
        "http://concstarfront.vercel.app/",
        "concstarfront.vercel.app"
    ] + settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(CustomBusinessException, business_exception_handler)  # type: ignore

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}


# Register Routers
from app.routers import user_router, constancy_router, question_router, configuration_router, session_router, auth_router

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(constancy_router.router)
app.include_router(question_router.router)
app.include_router(configuration_router.router)
app.include_router(session_router.router)
