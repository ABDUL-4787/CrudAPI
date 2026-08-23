from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from typing import List

def generate_task_pdf(user_email: str, tasks: List[dict]) -> bytes:
    buffer = BytesIO()
    
    # Set up document layout
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    story = []
    
    # Create Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=15
    )
    section_title_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#2B6CB0"),
        spaceAfter=10
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=10,
        spaceAfter=6
    )
    bold_body_style = ParagraphStyle(
        "ReportBodyBold",
        parent=body_style,
        fontName="Helvetica-Bold"
    )
    
    # Add Document Title
    story.append(Paragraph("TaskFlow AI — Tasks Summary Report", title_style))
    story.append(Spacer(1, 10))
    
    # Calculate Statistics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t["done"])
    pending_tasks = total_tasks - completed_tasks
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S (local)")
    
    # User Metadata
    story.append(Paragraph(f"<b>User Email:</b> {user_email}", body_style))
    story.append(Paragraph(f"<b>Generated On:</b> {timestamp}", body_style))
    story.append(Spacer(1, 10))
    
    # Stats Overview Grid
    stats_data = [
        [
            Paragraph("<b>Total Tasks</b>", body_style),
            Paragraph("<b>Completed Tasks</b>", body_style),
            Paragraph("<b>Pending Tasks</b>", body_style)
        ],
        [
            str(total_tasks),
            str(completed_tasks),
            str(pending_tasks)
        ]
    ]
    stats_table = Table(stats_data, colWidths=[150, 150, 150])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 20))
    
    # Task Details Table
    story.append(Paragraph("Task Details", section_title_style))
    
    table_data = [
        [
            Paragraph("<b><font color='white'>ID</font></b>", bold_body_style),
            Paragraph("<b><font color='white'>Title</font></b>", bold_body_style),
            Paragraph("<b><font color='white'>Status</font></b>", bold_body_style)
        ]
    ]
    
    for task in tasks:
        status_text = "<font color='green'>Completed</font>" if task["done"] else "<font color='red'>Pending</font>"
        table_data.append([
            str(task["id"]),
            Paragraph(task["title"], body_style),
            Paragraph(status_text, body_style)
        ])
    
    # Total width is 532 (612 page width - 80 margin)
    task_table = Table(table_data, colWidths=[60, 352, 120])
    task_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (2,0), (2,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(task_table)
    
    # Build PDF
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
