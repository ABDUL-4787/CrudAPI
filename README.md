# Supabase Auth: Login & Protect API Backend

A simple and clean FastAPI backend implementing authentication and route protection using **Supabase Auth**. This project demonstrates signing up users, managing sessions (login/logout), and applying reusable dependencies to protect secure routes.

---

## Technologies Used
- **Python 3.10+**
- **FastAPI**: Modern high-performance web framework.
- **Supabase Python Client**: Official SDK to communicate with the Supabase GoTrue Auth server.
- **Python Dotenv**: Configuration management using local environment files.

---

## Required Environment Variables
To authenticate with Supabase, you must define these variables in your `.env` configuration file:

*   `SUPABASE_URL`: The API URL of your Supabase project (e.g., `https://your-project-id.supabase.co`).
*   `SUPABASE_KEY`: The anon public key of your Supabase project.

---

## Setup & Installation Instructions

### 1. Configure the Environment
Generate your local `.env` file from the template:
```bash
cp .env.example .env
```
Open `.env` and fill in your active Supabase project credentials.

### 2. Install Project Dependencies
Activate your virtual environment and install the required Python packages:
```powershell
# Activate local virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

### 3. Run the Server
Launch the FastAPI development server:
```powershell
uvicorn main:app --reload
```
The server will start at: **http://127.0.0.1:8000**

---

## API Endpoints Summary

| Method | Endpoint | Authentication Required | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/` | No | Simple welcome API page |
| `GET` | `/public/info` | No | Unprotected public welcome information |
| `POST`| `/auth/signup` | No | Register a new user with email and password |
| `POST`| `/auth/login` | No | Log in and retrieve the `access_token` and `refresh_token` |
| `POST`| `/auth/logout`| **Yes (Bearer)** | Signs the user session out |
| `GET` | `/protected/profile`| **Yes (Bearer)** | Returns basic profile information of the active user |
| `GET` | `/protected/dashboard`| **Yes (Bearer)** | Access-protected dashboard page |

---

## How to Test in Swagger UI (`/docs`)

1. Open your web browser and navigate to: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
2. First, register a new test user by expanding `POST /auth/signup`, clicking **Try it out**, filling in an email/password, and clicking **Execute**.
3. Log in by expanding `POST /auth/login`, clicking **Try it out**, using the same email/password, and clicking **Execute**.
4. Copy the long `access_token` string returned in the response body.
5. Scroll back to the top of the Swagger page and click the green **Authorize** padlock button.
6. In the value input field, paste the copied token (FastAPI automatically prefixes it with `Bearer`) and click **Authorize**.
7. Now, expand any protected endpoint (like `GET /protected/profile` or `GET /protected/dashboard`), click **Try it out**, and click **Execute**. You will see the authenticated user metadata!
8. When finished, you can run `POST /auth/logout` while authenticated to invalidate the session.

---

## Swagger UI Screenshot Placeholder
*Insert your Swagger UI screenshot here showing the padlock lock symbols and Authorize configurations:*

```text
[INSERT SCREENSHOT PLACEHOLDER HERE]
```
