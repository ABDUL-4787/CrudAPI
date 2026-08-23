from fastapi import FastAPI, Request, status, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

app = FastAPI(
    title="To-Do CRUD API",
    description="A complete, minimal CRUD To-Do API built with FastAPI.",
    version="1.0.0"
)

# In-memory tasks database
tasks_db = [
    {
        "id": 1,
        "title": "Buy groceries",
        "description": "Buy milk, eggs, bread, and fruits",
        "completed": False
    },
    {
        "id": 2,
        "title": "Clean the house",
        "description": "Vacuum the living room and dust the shelves",
        "completed": True
    },
    {
        "id": 3,
        "title": "Learn FastAPI",
        "description": "Practice building APIs and writing tests",
        "completed": False
    }
]

# Track next task ID
next_id = 4

# Pydantic Models
class TaskCreate(BaseModel):
    title: str = Field(..., description="The title of the task (required, non-empty)")
    description: Optional[str] = Field(None, description="Optional detailed description")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title must not be empty or whitespace-only.")
        return v

class TaskUpdate(BaseModel):
    title: str = Field(..., description="The title of the task (required, non-empty)")
    description: Optional[str] = Field(None, description="Optional detailed description")
    completed: bool = Field(..., description="Completion status of the task")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title must not be empty or whitespace-only.")
        return v

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool

# Custom Exception Handler to return HTTP 400 for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    
    # Check if there is an error specifically related to the field "title"
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
            # Strip Pydantic's default "Value error, " prefix
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, "):]
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": msg}
        )

    # Generic validation error message for other fields or payloads
    first_err = errors[0] if errors else {}
    msg = first_err.get("msg", "Validation error")
    loc = first_err.get("loc", ["field"])
    field = loc[-1] if loc else "field"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": f"Invalid value for '{field}': {msg}"}
    )

# Routes
@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"message": "Welcome to the To-Do CRUD API!"}

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

@app.get("/tasks", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def get_tasks():
    return tasks_db

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"Task with ID {task_id} not found"}
    )

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate):
    global next_id
    new_task = {
        "id": next_id,
        "title": task_in.title.strip(),
        "description": task_in.description.strip() if task_in.description else None,
        "completed": False
    }
    tasks_db.append(new_task)
    next_id += 1
    return new_task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate):
    for task in tasks_db:
        if task["id"] == task_id:
            task["title"] = task_in.title.strip()
            task["description"] = task_in.description.strip() if task_in.description else None
            task["completed"] = task_in.completed
            return task
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"Task with ID {task_id} not found"}
    )

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    for i, task in enumerate(tasks_db):
        if task["id"] == task_id:
            tasks_db.pop(i)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"Task with ID {task_id} not found"}
    )
