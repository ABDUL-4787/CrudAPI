from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.database import get_db
from app.services.llm_service import analyze_tasks_with_llm

router = APIRouter(prefix="/tasks", tags=["AI Integration"])

@router.post("/analyze")
def analyze_tasks(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    # Query user's current tasks
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, done FROM tasks WHERE user_id = %s ORDER BY id ASC;",
                (user_id,)
            )
            rows = cursor.fetchall()
            tasks = [dict(row) for row in rows]
            
    # Send tasks to LLM analysis helper
    analysis = analyze_tasks_with_llm(tasks)
    return analysis
