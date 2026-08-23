from fastapi import APIRouter, Depends, Response
from app.auth import get_current_user
from app.database import get_db
from app.services.report_service import generate_task_pdf

router = APIRouter(prefix="/reports", tags=["Reporting"])

@router.get("/tasks/pdf")
def download_tasks_pdf(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    user_email = current_user["email"]
    
    # Fetch all tasks owned by the current user
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, done FROM tasks WHERE user_id = %s ORDER BY id ASC;",
                (user_id,)
            )
            rows = cursor.fetchall()
            tasks = [dict(row) for row in rows]
            
    # Render PDF bytes using ReportLab service
    pdf_content = generate_task_pdf(user_email, tasks)
    
    # Return streaming attachment response
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=tasks_report_{user_id}.pdf"
        }
    )
