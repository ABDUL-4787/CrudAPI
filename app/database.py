import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Build database connection URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_name = os.getenv("DB_NAME", "todo_db")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL
                    );
                """)
                
                # Create tasks table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        done BOOLEAN NOT NULL DEFAULT FALSE,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Seed test user if users table is empty (password is 'password123')
                cursor.execute("SELECT COUNT(*) AS cnt FROM users;")
                user_count = cursor.fetchone()["cnt"]
                if user_count == 0:
                    cursor.execute(
                        "INSERT INTO users (id, email, hashed_password) VALUES (%s, %s, %s);",
                        (1, "test@example.com", "$2b$12$SE5Tntw0o9Hyguz5/OegoO3YCYPJ09BKoXZT5sMEQNZ5RpEPl1woW")
                    )
                    # Reset user sequence
                    cursor.execute("SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 1));")
                
                # Seed exactly 3 example tasks only when tasks table is empty
                cursor.execute("SELECT COUNT(*) AS cnt FROM tasks;")
                task_count = cursor.fetchone()["cnt"]
                if task_count == 0:
                    cursor.execute("INSERT INTO tasks (title, done, user_id) VALUES ('Buy groceries', FALSE, 1);")
                    cursor.execute("INSERT INTO tasks (title, done, user_id) VALUES ('Clean the house', TRUE, 1);")
                    cursor.execute("INSERT INTO tasks (title, done, user_id) VALUES ('Learn FastAPI', FALSE, 1);")
                
                conn.commit()
    except Exception as e:
        print(f"Warning: Local database connection/initialization skipped or failed: {e}")

# Initialize database on load
init_db()
