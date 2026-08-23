from fastapi import FastAPI, Request, status, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load env variables from .env if it exists
load_dotenv()

# Build database connection URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_name = os.getenv("DB_NAME", "todo_db")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

app = FastAPI(
    title="To-Do CRUD API",
    description="A complete, minimal PostgreSQL-backed CRUD To-Do API built with FastAPI.",
    version="3.0.0"
)

# Helper function to get database connection
def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# Database Initialization
def init_db():
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        done BOOLEAN NOT NULL DEFAULT FALSE
                    );
                """)
                
                # Check if empty
                cursor.execute("SELECT COUNT(*) AS cnt FROM tasks;")
                row = cursor.fetchone()
                if row and row["cnt"] == 0:
                    cursor.execute("INSERT INTO tasks (title, done) VALUES ('Buy groceries', FALSE);")
                    cursor.execute("INSERT INTO tasks (title, done) VALUES ('Clean the house', TRUE);")
                    cursor.execute("INSERT INTO tasks (title, done) VALUES ('Learn FastAPI', FALSE);")
                conn.commit()
    except Exception as e:
        print(f"Warning: Local database connection/initialization skipped or failed: {e}")

# Initialize database on load (primarily for local execution)
init_db()

# Helper to convert Row dict
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
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks ORDER BY id ASC;")
            rows = cursor.fetchall()
            return [row_to_task(row) for row in rows]

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s;", (task_id,))
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
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done;",
                (task_in.title.strip(), False)
            )
            row = cursor.fetchone()
            conn.commit()
            return row_to_task(row)

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done;",
                (task_in.title.strip(), task_in.done, task_id)
            )
            row = cursor.fetchone()
            if row:
                conn.commit()
                return row_to_task(row)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"Task with ID {task_id} not found"}
    )

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s RETURNING id;", (task_id,))
            row = cursor.fetchone()
            if row:
                conn.commit()
                return Response(status_code=status.HTTP_204_NO_CONTENT)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"Task with ID {task_id} not found"}
    )
