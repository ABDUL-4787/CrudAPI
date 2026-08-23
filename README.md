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

### Root Endpoint (`GET /`)

#### Command:
```bash
curl -i http://127.0.0.1:8000/
```

#### Expected Output:
```http
HTTP/1.1 200 OK
content-type: application/json

{"message":"Welcome to the To-Do CRUD API!"}
```

### Health Check Endpoint (`GET /health`)

#### Command:
```bash
curl -i http://127.0.0.1:8000/health
```

#### Expected Output:
```http
HTTP/1.1 200 OK
content-type: application/json

{"status":"ok"}
```

### Retrieve All Tasks (`GET /tasks`)

#### Command:
```bash
curl -i http://127.0.0.1:8000/tasks
```

#### Expected Output:
```http
HTTP/1.1 200 OK
content-type: application/json

[
  {"id":1,"title":"Buy groceries","description":"Buy milk, eggs, bread, and fruits","completed":false},
  {"id":2,"title":"Clean the house","description":"Vacuum the living room and dust the shelves","completed":true},
  {"id":3,"title":"Learn FastAPI","description":"Practice building APIs and writing tests","completed":false}
]
```

### Retrieve a Single Task (`GET /tasks/{id}`)

#### Command:
```bash
curl -i http://127.0.0.1:8000/tasks/1
```

#### Expected Output:
```http
HTTP/1.1 200 OK
content-type: application/json

{"id":1,"title":"Buy groceries","description":"Buy milk, eggs, bread, and fruits","completed":false}
```

### Task Not Found (`GET /tasks/{id}` with Unknown ID)

#### Command:
```bash
curl -i http://127.0.0.1:8000/tasks/999
```

#### Expected Output:
```http
HTTP/1.1 404 Not Found
content-type: application/json

{"error":"Task with ID 999 not found"}
```

### Create a Task (`POST /tasks`)

Creating a task requires a valid JSON payload. A successful creation returns **HTTP 201 Created** along with the created task object. 

If the `title` field is missing, empty, or consists only of whitespace, the API rejects the request with **HTTP 400 Bad Request** and returns a JSON response containing an `"error"` field detailing the validation failure.

#### Example Request (Success):
```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Write Unit Tests", "description": "Verify all API endpoints work as expected"}'
```

#### Expected Output (HTTP 201 Created):
```http
HTTP/1.1 201 Created
date: Sun, 23 Aug 2026 10:25:00 GMT
server: uvicorn
content-length: 104
content-type: application/json

{"id":4,"title":"Write Unit Tests","description":"Verify all API endpoints work as expected","completed":false}
```

#### Example Request (Missing, Empty, or Whitespace Title):
```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "   ", "description": "Whitespace title"}'
```

#### Expected Output (HTTP 400 Bad Request):
```http
HTTP/1.1 400 Bad Request
date: Sun, 23 Aug 2026 10:25:05 GMT
server: uvicorn
content-length: 51
content-type: application/json

{"error":"Title must not be empty or whitespace-only."}
```

### Update a Task (`PUT /tasks/{id}`)

Updating a task replaces its contents. A successful update returns **HTTP 200 OK** with the updated task object. 

- If the task ID does not exist, it returns **HTTP 404 Not Found** with a JSON response containing an `"error"` field.
- If the `title` field is empty or whitespace-only, it returns **HTTP 400 Bad Request** with an `"error"` field.

#### Example Request:
```bash
curl -i -X PUT http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy fresh groceries", "description": "Milk, eggs, and bread", "completed": true}'
```

#### Expected Output (HTTP 200 OK):
```http
HTTP/1.1 200 OK
content-type: application/json

{"id":1,"title":"Buy fresh groceries","description":"Milk, eggs, and bread","completed":true}
```

#### Expected Output for Unknown ID (HTTP 404 Not Found):
```http
HTTP/1.1 404 Not Found
content-type: application/json

{"error":"Task with ID 999 not found"}
```

### Delete a Task (`DELETE /tasks/{id}`)

Deleting a task removes it from the database. A successful deletion returns **HTTP 204 No Content** with an empty response body.

- If the task ID does not exist, it returns **HTTP 404 Not Found** with a JSON response containing an `"error"` field.

#### Example Request:
```bash
curl -i -X DELETE http://127.0.0.1:8000/tasks/1
```

#### Expected Output (HTTP 204 No Content):
```http
HTTP/1.1 204 No Content
```

#### Expected Output for Unknown ID (HTTP 404 Not Found):
```http
HTTP/1.1 404 Not Found
content-type: application/json

{"error":"Task with ID 999 not found"}
```

---

## Complete CRUD Flow Example

Here is a quick, complete lifecycle of a task from creation to deletion:

1. **Create** the task:
   ```bash
   curl -s -X POST http://127.0.0.1:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Review PRs"}'
   ```
   *Response:* `{"id":4,"title":"Review PRs","description":null,"completed":false}`

2. **Read** the created task:
   ```bash
   curl -s http://127.0.0.1:8000/tasks/4
   ```
   *Response:* `{"id":4,"title":"Review PRs","description":null,"completed":false}`

3. **Update** the task to completed:
   ```bash
   curl -s -X PUT http://127.0.0.1:8000/tasks/4 \
     -H "Content-Type: application/json" \
     -d '{"title": "Review PRs", "completed": true}'
   ```
   *Response:* `{"id":4,"title":"Review PRs","description":null,"completed":true}`

4. **Delete** the task:
   ```bash
   curl -i -X DELETE http://127.0.0.1:8000/tasks/4
   ```
   *Response:* `HTTP/1.1 204 No Content` (Empty body)

