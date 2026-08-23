from fastapi import FastAPI, Request, status, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import sqlite3
import os

DATABASE = "tasks.db"

app = FastAPI(
    title="To-Do CRUD API",
    description="A complete, minimal SQLite-backed CRUD To-Do API built with FastAPI.",
    version="2.0.0"
)

# Helper function to get database connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Database Initialization
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            );
        """)
        
        # Seed only if table is empty
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks;")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute("INSERT INTO tasks (title, done) VALUES ('Buy groceries', 0);")
            cursor.execute("INSERT INTO tasks (title, done) VALUES ('Clean the house', 1);")
            cursor.execute("INSERT INTO tasks (title, done) VALUES ('Learn FastAPI', 0);")
            conn.commit()

# Initialize the database immediately on module load
init_db()

# Helper to convert Row to dict
def row_to_task(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }

# Pydantic Models
class TaskCreate(BaseModel):
    title: str = Field(..., description="The title of the task (required, non-empty)")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title must not be empty or whitespace-only.")
        return v

class TaskUpdate(BaseModel):
    title: str = Field(..., description="The title of the task (required, non-empty)")
    done: bool = Field(..., description="Completion status of the task")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title must not be empty or whitespace-only.")
        return v

class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool

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
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks;")
        rows = cursor.fetchall()
        return [row_to_task(row) for row in rows]

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?;", (task_id,))
        row = cursor.fetchone()
        if row:
            return row_to_task(row)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"Task with ID {task_id} not found"}
    )

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (?, 0);",
            (task_in.title.strip(),)
        )
        new_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?;", (new_id,))
        row = cursor.fetchone()
        return row_to_task(row)

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tasks WHERE id = ?;", (task_id,))
        if not cursor.fetchone():
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": f"Task with ID {task_id} not found"}
            )
        
        cursor.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?;",
            (task_in.title.strip(), 1 if task_in.done else 0, task_id)
        )
        conn.commit()
        
        cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?;", (task_id,))
        row = cursor.fetchone()
        return row_to_task(row)

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tasks WHERE id = ?;", (task_id,))
        if not cursor.fetchone():
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": f"Task with ID {task_id} not found"}
            )
        
        cursor.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
        conn.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
