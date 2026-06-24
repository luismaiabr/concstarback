from fastapi import Request
from fastapi.responses import JSONResponse

class CustomBusinessException(Exception):
    def __init__(self, status_code: int, error_code: str, message: str):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message

async def global_exception_handler(request: Request, exc: Exception):
    # Log the real error to external tools (Sentry, Datadog etc) here if needed
    return JSONResponse(
        status_code=500,
        content={"error_code": "INTERNAL_SERVER_ERROR", "message": "Um erro inesperado ocorreu."}
    )

async def business_exception_handler(request: Request, exc: CustomBusinessException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.message}
    )
