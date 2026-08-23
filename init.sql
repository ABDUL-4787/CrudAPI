CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed test user if users table is empty (password is 'password123')
INSERT INTO users (id, email, hashed_password)
SELECT 1, 'test@example.com', '$2b$12$SE5Tntw0o9Hyguz5/OegoO3YCYPJ09BKoXZT5sMEQNZ5RpEPl1woW'
WHERE (SELECT COUNT(*) FROM users) = 0;

-- Reset sequence for users
SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 1));

-- Seed exactly 3 example tasks only when the tasks table is empty
INSERT INTO tasks (title, done, user_id)
SELECT title, done, 1
FROM (
    VALUES 
        ('Buy groceries', FALSE),
        ('Clean the house', TRUE),
        ('Learn FastAPI', FALSE)
) AS seed(title, done)
WHERE (SELECT COUNT(*) FROM tasks) = 0;
