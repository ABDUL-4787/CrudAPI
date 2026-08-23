import os
import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import List

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "ai_usage.log")

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

def analyze_tasks_with_llm(tasks: List[dict]) -> dict:
    # Construct task text representation
    task_lines = []
    for t in tasks:
        status = "Completed" if t["done"] else "Pending"
        task_lines.append(f"- ID {t['id']}: '{t['title']}' ({status})")
    
    tasks_text = "\n".join(task_lines) if task_lines else "No tasks currently on the list."
    
    # Prompt instructing raw JSON back to the API
    prompt = f"""
    You are an AI Task Flow Productivity Assistant. Analyze the following user tasks and return a structured analysis.
    
    User Tasks:
    {tasks_text}
    
    Your response must be valid JSON matching this exact structure:
    {{
        "summary": "A concise 1-2 sentence productivity summary.",
        "priorities": [
            "List 2-3 specific recommendations on which tasks to do first and why."
        ]
    }}
    
    Provide ONLY the raw JSON output. Do not wrap it in markdown block quotes (such as ```json) or add other conversational text.
    """
    
    # Fallback to local mockup if dummy API key or no key is present
    if not GEMINI_API_KEY or GEMINI_API_KEY == "dummy_gemini_key" or GEMINI_API_KEY == "your_gemini_api_key_here":
        mock_response = {
            "summary": "You have a solid task list with a mix of pending and completed items. Focus on finishing outstanding learning and shopping tasks.",
            "priorities": [
                "1. Buy groceries (ID 1) - Essential for daily living.",
                "2. Learn FastAPI (ID 3) - Important for skill building."
            ]
        }
        # Log mock token consumption
        log_ai_usage(len(prompt) // 4, 150, 0.0)
        return mock_response

    # Direct Google Gemini API POST request (no heavy SDK needed)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            result = json.loads(response.read().decode("utf-8"))
            text_response = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            # Remove potential markdown block wrappers
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            text_response = text_response.strip()
            
            parsed_data = json.loads(text_response)
            
            # Simple validation to ensure structure is intact
            if "summary" not in parsed_data or "priorities" not in parsed_data:
                raise ValueError("Response lacks required JSON keys.")
            
            # Cost Calculation
            input_tokens = len(prompt) // 4
            output_tokens = len(text_response) // 4
            # Gemini 1.5 Flash rates: $0.075 / 1M input tokens, $0.30 / 1M output tokens
            cost = ((input_tokens / 1_000_000) * 0.075) + ((output_tokens / 1_000_000) * 0.30)
            
            log_ai_usage(input_tokens, output_tokens, cost)
            return parsed_data
            
    except Exception as e:
        print(f"Error calling LLM API: {e}")
        # Standard error response fallback
        return {
            "summary": "Productivity analysis is temporarily unavailable. Please try again later.",
            "priorities": ["No priority recommendations available due to service communication failure."]
        }

def log_ai_usage(input_tokens: int, output_tokens: int, cost: float):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Input: {input_tokens} tokens | Output: {output_tokens} tokens | Est Cost: ${cost:.8f}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing cost log: {e}")
