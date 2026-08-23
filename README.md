# Minimal CRUD To-Do API

A lightweight, complete CRUD (Create, Read, Update, Delete) To-Do API built using Python and FastAPI. It stores all tasks in-memory and features clean error handling, strict validation, and an interactive Swagger UI.

> [!WARNING]
> This application uses an in-memory list to store tasks. All data will be reset when the server restarts.

---

## Features

- **Lightweight Stack**: Built using only FastAPI, Uvicorn, and standard Python libraries (no database or external dependencies).
- **Interactive API Documentation**: Out-of-the-box Swagger UI (interactive documentation) and ReDoc.
- **Robust Validation**: Invalid or empty input fields (like missing or empty titles) are validation-checked and return `400 Bad Request` with custom error payloads.
- **Status Codes**: Follows REST conventions using proper HTTP status codes: `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, and `404 Not Found`.

---

## Installation & Running

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your system.

### 2. Setup Virtual Environment
Clone/copy the project and run the following commands in your terminal to set up the virtual environment and install dependencies:

```bash
# Create the virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.venv\Scripts\activate.bat
# On macOS/Linux:
source .venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 3. Start the Server
Run the FastAPI development server using Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

---

## API Endpoints

| Method | Endpoint | Success Code | Error Codes | Description |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/` | `200 OK` | - | Welcome message |
| **GET** | `/health` | `200 OK` | - | Service health status check |
| **GET** | `/tasks` | `200 OK` | - | Retrieve list of all tasks |
| **GET** | `/tasks/{id}` | `200 OK` | `404 Not Found` | Retrieve a single task by its ID |
| **POST** | `/tasks` | `201 Created` | `400 Bad Request` | Create a new task |
| **PUT** | `/tasks/{id}` | `200 OK` | `400 Bad Request`, `404 Not Found` | Update an existing task |
| **DELETE** | `/tasks/{id}` | `204 No Content`| `404 Not Found` | Delete a task |

---

## Swagger UI Documentation

FastAPI provides interactive Swagger UI documentation at:
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

You can use the **Try it out** button in the Swagger UI to test the CRUD cycle (GET, POST, PUT, DELETE) directly from your browser.

---

## Example Usage

### Create a Task (`POST /tasks`)

#### Command:
```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Write Unit Tests", "description": "Verify all API endpoints work as expected"}'
```

#### Expected Output:
```http
HTTP/1.1 201 Created
date: Sun, 23 Aug 2026 10:25:00 GMT
server: uvicorn
content-length: 104
content-type: application/json

{"id":4,"title":"Write Unit Tests","description":"Verify all API endpoints work as expected","completed":false}
```

### Invalid Title Example (`POST /tasks` with Empty Title)

#### Command:
```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "   ", "description": "Whitespace title"}'
```

#### Expected Output:
```http
HTTP/1.1 400 Bad Request
date: Sun, 23 Aug 2026 10:25:05 GMT
server: uvicorn
content-length: 51
content-type: application/json

{"error":"Title must not be empty or whitespace-only."}
```
