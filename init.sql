CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);

-- Seed exactly 3 tasks only when the table is empty
INSERT INTO tasks (title, done)
SELECT title, done
FROM (
    VALUES 
        ('Buy groceries', FALSE),
        ('Clean the house', TRUE),
        ('Learn FastAPI', FALSE)
) AS seed(title, done)
WHERE (SELECT COUNT(*) FROM tasks) = 0;
