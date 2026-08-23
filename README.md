# SQLite-Backed CRUD To-Do API

A lightweight, complete CRUD (Create, Read, Update, Delete) To-Do API built using Python, FastAPI, and a local SQLite database. It features clean error handling, strict validation, and an interactive Swagger UI.

---

## Why SQLite?
SQLite was chosen for this project because:
- **Zero Configuration**: It requires no external server setup, installation, or administration.
- **Self-Contained**: The entire database is stored in a single cross-platform disk file.
- **Built-in Python Integration**: Python comes with the `sqlite3` library in its standard library, avoiding external dependency overhead.
- **Lightweight & Fast**: Perfect for minimal and developer-friendly local setups.

---

## Database Location
The database is automatically created and stored in the project root directory as a file named:
`tasks.db`

---

## Installation & Running

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your system.

### 2. Setup Virtual Environment
Run the following commands in your terminal to set up the virtual environment and install dependencies:

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

The database (`tasks.db`) will be automatically initialized and seeded with 3 example tasks if it does not already exist. The API is hosted at: `http://127.0.0.1:8000`

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

## Database Schema & Query Example

The database table `tasks` is structured as follows:
```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT 0
);
```

## SQL Queries Explored

Here are some key SQLite queries used and explored in this project:

- **Select all tasks**:
  ```sql
  SELECT * FROM tasks;
  ```
- **Select completed tasks**:
  ```sql
  SELECT * FROM tasks WHERE done = 1;
  ```
- **Count the total number of tasks**:
  ```sql
  SELECT COUNT(*) FROM tasks;
  ```
- **Mark all tasks as completed**:
  ```sql
  UPDATE tasks SET done = 1;
  ```
- **Delete all completed tasks**:
  ```sql
  DELETE FROM tasks WHERE done = 1;
  ```

---

## Database Viewer
_Below is a placeholder for a database viewer screenshot showing the seeded tasks in `tasks.db`:_

![Database Viewer Screenshot Placeholder](https://raw.githubusercontent.com/ABDUL-4787/CrudAPI/main/docs/db_viewer_placeholder.png)

---

## Swagger UI Documentation

Swagger UI is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). 

All endpoints can be tested interactively there, allowing you to perform a full CRUD cycle using the "Try it out" button on each endpoint.

---

## Example Usage

### Root Endpoint (`GET /`)
```bash
curl -i http://127.0.0.1:8000/
```
```http
HTTP/1.1 200 OK
content-type: application/json

{"message":"Welcome to the To-Do CRUD API!"}
```

### Health Check Endpoint (`GET /health`)
```bash
curl -i http://127.0.0.1:8000/health
```
```http
HTTP/1.1 200 OK
content-type: application/json

{"status":"ok"}
```

### Retrieve All Tasks (`GET /tasks`)
```bash
curl -i http://127.0.0.1:8000/tasks
```
```http
HTTP/1.1 200 OK
content-type: application/json

[
  {"id":1,"title":"Buy groceries","done":false},
  {"id":2,"title":"Clean the house","done":true},
  {"id":3,"title":"Learn FastAPI","done":false}
]
```

### Retrieve a Single Task (`GET /tasks/{id}`)
```bash
curl -i http://127.0.0.1:8000/tasks/1
```
```http
HTTP/1.1 200 OK
content-type: application/json

{"id":1,"title":"Buy groceries","done":false}
```

### Task Not Found (`GET /tasks/{id}` with Unknown ID)
```bash
curl -i http://127.0.0.1:8000/tasks/999
```
```http
HTTP/1.1 404 Not Found
content-type: application/json

{"error":"Task with ID 999 not found"}
```

### Create a Task (`POST /tasks`)
```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Write Unit Tests"}'
```
```http
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Write Unit Tests","done":false}
```

### Invalid Title Example (`POST /tasks` with Empty Title)
```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "   "}'
```
```http
HTTP/1.1 400 Bad Request
content-type: application/json

{"error":"Title must not be empty or whitespace-only."}
```

### Update a Task (`PUT /tasks/{id}`)
```bash
curl -i -X PUT http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy fresh groceries", "done": true}'
```
```http
HTTP/1.1 200 OK
content-type: application/json

{"id":1,"title":"Buy fresh groceries","done":true}
```

### Delete a Task (`DELETE /tasks/{id}`)
```bash
curl -i -X DELETE http://127.0.0.1:8000/tasks/1
```
```http
HTTP/1.1 204 No Content
```

---

## Complete CRUD Flow Example

1. **Create** the task:
   ```bash
   curl -s -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d '{"title": "Review PRs"}'
   ```
   *Response:* `{"id":4,"title":"Review PRs","done":false}`

2. **Read** the created task:
   ```bash
   curl -s http://127.0.0.1:8000/tasks/4
   ```
   *Response:* `{"id":4,"title":"Review PRs","done":false}`

3. **Update** the task to done:
   ```bash
   curl -s -X PUT http://127.0.0.1:8000/tasks/4 -H "Content-Type: application/json" -d '{"title": "Review PRs", "done": true}'
   ```
   *Response:* `{"id":4,"title":"Review PRs","done":true}`

4. **Delete** the task:
   ```bash
   curl -i -X DELETE http://127.0.0.1:8000/tasks/4
   ```
   *Response:* `HTTP/1.1 204 No Content` (Empty body)
