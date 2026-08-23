from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routes.auth import router as auth_router
from app.routes.tasks import router as tasks_router
from app.routes.reports import router as reports_router
from app.routes.ai import router as ai_router

app = FastAPI(
    title="TaskFlow AI Backend",
    description="TaskFlow AI — AI-Powered Task Management Capstone Backend.",
    version="1.0.0"
)

# Custom Validation Override Exception Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    
    # Check for title errors
    title_err = None
    for err in errors:
        if "title" in err.get("loc", []):
            title_err = err
            break

    if title_err:
        err_type = title_err.get("type")
        if err_type == "missing":
            msg = "Title is required."
        else:
            msg = title_err.get("msg", "Title is invalid.")
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, "):]
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": msg}
        )

    # Generic validation error message fallback
    first_err = errors[0] if errors else {}
    msg = first_err.get("msg", "Validation error")
    loc = first_err.get("loc", ["field"])
    field = loc[-1] if loc else "field"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": f"Invalid value for '{field}': {msg}"}
    )

# Root Endpoints (Preserving previous assignments structure)
@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"message": "Welcome to the To-Do CRUD API!"}

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

# Register Modular Routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(reports_router)
app.include_router(ai_router)
