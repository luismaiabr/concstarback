from fastapi import FastAPI
from app.core.exceptions import global_exception_handler, business_exception_handler, CustomBusinessException

app = FastAPI(
    title="Concstar Backend",
    description="Backend API for Concstar",
    version="0.1.0",
)

# Register Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(CustomBusinessException, business_exception_handler)  # type: ignore

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}

# Register Routers
from app.routers import user_router, constancy_router, question_router, configuration_router, session_router

app.include_router(user_router.router)
app.include_router(constancy_router.router)
app.include_router(question_router.router)
app.include_router(configuration_router.router)
app.include_router(session_router.router)
