from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks
from typing import List
from app.auth import get_current_user
from app.database import get_db
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.services.cache import get_cached_tasks, set_cached_tasks, invalidate_cached_tasks
from datetime import datetime
import os

router = APIRouter(prefix="/tasks", tags=["Tasks Management"])
STATS_FILE = "logs/task_statistics.log"

# Create logs directory if not exists
os.makedirs("logs", exist_ok=True)

# Background task to record statistics
def log_task_change(user_id: int, action: str, task_id: int):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] User {user_id} performed '{action}' on Task ID {task_id}\n"
        with open(STATS_FILE, "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Warning: Background statistics logging failed: {e}")

@router.get("", response_model=List[TaskResponse])
def get_tasks(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    # 1. Attempt to hit cache
    cached = get_cached_tasks(user_id)
    if cached is not None:
        return cached

    # 2. Query database on cache miss
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, done, user_id FROM tasks WHERE user_id = %s ORDER BY id ASC;",
                (user_id,)
            )
            rows = cursor.fetchall()
            tasks = [dict(row) for row in rows]
            
            # 3. Store in cache
            set_cached_tasks(user_id, tasks)
            return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, done, user_id FROM tasks WHERE id = %s AND user_id = %s;",
                (task_id, user_id)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
                
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {task_id} not found."
    )

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tasks (title, done, user_id) VALUES (%s, %s, %s) RETURNING id, title, done, user_id;",
                (task_in.title.strip(), False, user_id)
            )
            row = cursor.fetchone()
            conn.commit()
            
            task = dict(row)
            # Invalidate Redis cache
            invalidate_cached_tasks(user_id)
            # Queue background log task
            background_tasks.add_task(log_task_change, user_id, "CREATE", task["id"])
            return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            # Check ownership and update
            cursor.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s AND user_id = %s RETURNING id, title, done, user_id;",
                (task_in.title.strip(), task_in.done, task_id, user_id)
            )
            row = cursor.fetchone()
            if row:
                conn.commit()
                task = dict(row)
                
                # Invalidate cache
                invalidate_cached_tasks(user_id)
                # Queue background log task
                background_tasks.add_task(log_task_change, user_id, "UPDATE", task["id"])
                return task
                
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {task_id} not found."
    )

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM tasks WHERE id = %s AND user_id = %s RETURNING id;",
                (task_id, user_id)
            )
            row = cursor.fetchone()
            if row:
                conn.commit()
                # Invalidate cache
                invalidate_cached_tasks(user_id)
                # Queue background log task
                background_tasks.add_task(log_task_change, user_id, "DELETE", task_id)
                return Response(status_code=status.HTTP_204_NO_CONTENT)
                
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {task_id} not found."
    )
