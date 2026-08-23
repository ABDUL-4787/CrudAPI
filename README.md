# Dockerized PostgreSQL CRUD To-Do API

A lightweight, complete CRUD (Create, Read, Update, Delete) To-Do API built using Python, FastAPI, and PostgreSQL running in Docker containers. 

The API routes and service behavior remain completely unchanged from previous stages, but the backend storage layer has been fully migrated to PostgreSQL, managed via Docker Compose.

---

## Architecture Overview
The application consists of two containerized services orchestrated by Docker Compose:
- **`web`**: The FastAPI application containerized using a lightweight python image.
- **`db`**: A PostgreSQL 15 database service configured with schema auto-initialization and seeding.

---

## Database Persistence
To ensure that data survives container lifecycles, database persistence is handled using a **named Docker Volume** (`pgdata`):
- The volume maps container directory `/var/lib/postgresql/data` directly to a persistent location on the host machine.
- Stopping or recreating the containers with `docker compose down` will **not** destroy the database content; your tasks remain safe and persist across container builds and restarts.

---

## Getting Started

### 1. Prerequisites
Ensure you have the following installed on your machine:
- [Docker](https://www.docker.com/) (Must be started/running before executing commands)
- [Docker Compose](https://docs.docker.com/compose/)

### 2. Configuration Setup (`.env`)
Create a local `.env` file from the provided `.env.example` to define configuration settings (note that the `.env` file is excluded from Git tracking for security):

```bash
# Copy env.example to create the local configuration file
cp .env.example .env
```

Open `.env` in an editor and set your password:
```env
DB_USER=postgres
DB_PASSWORD=your_secret_password
DB_NAME=todo_db
```

### 3. Launching the Services
To build the FastAPI application container, download the PostgreSQL service, and start both containers in the background, run:

```bash
docker compose up --build -d
```

Once started, the API will be available at:
- Root: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/health`
- Swagger UI Documentation: `http://127.0.0.1:8000/docs`

To stop the services, run:
```bash
docker compose down
```

---

## Swagger UI Documentation
All endpoints can be tested interactively by navigating to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and clicking the **Try it out** button on each route.

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

## How Persistence is Tested
To verify that the persistent volume is working correctly and data survives container restarts:

1. **Verify initial tasks** (seeded on start):
   ```bash
   curl -i http://127.0.0.1:8000/tasks
   ```
2. **Create a new task** (Task ID 4):
   ```bash
   curl -i -X POST http://127.0.0.1:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Docker Persistent Task"}'
   ```
3. **Restart the containers**:
   ```bash
   # Shut down the services (stops and removes containers, keeping volumes)
   docker compose down
   
   # Restart the services
   docker compose up -d
   ```
4. **Fetch tasks and verify data survival**:
   ```bash
   curl -i http://127.0.0.1:8000/tasks
   ```
   *Verify that "Docker Persistent Task" (with ID 4) is still present in the returned list.*

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

### Create a Task (`POST /tasks`)
```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Write Compose Config"}'
```
```http
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Write Compose Config","done":false}
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
