# postg.py

https://pypi.org/project/postg-q/0.1.0/

A minimal PostgreSQL database utility class using `psycopg2` with basic methods for interacting with a PostgreSQL database.

## Features

- Connect to PostgreSQL
- Create tables
- Insert records
- Select records (with optional filters)
- Update records (by condition)
- Delete records (by condition)
- Count rows
- Execute raw SQL queries with parameters

## Requirements

- Python 3.11+
- psycopg2
- python-dotenv (optional, for loading env variables)

## Installation

```bash
pip install postg-q


## Docs

1. Initialize and connect

from postg import DB

db = DB(
    dbname="your_db_name",
    user="your_user",
    password="your_password",
    host="localhost",
    port="5432"
)
db.connect()

2. Create a table

schema = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);
"""
db.create_table(schema)

3. Insert data

db.insert("users", {"name": "Alice", "email": "alice@example.com"})

4. Select data

users = db.select("users")
filtered = db.select("users", {"name": "Alice"})


5. Update records

db.update("users", filters={"name": "Alice"}, data={"email": "new@example.com"})

6. Delete records

db.delete("users", {"email": "new@example.com"})

7. Count rows

total = db.count("users")
filtered = db.count("users", {"name": "Bob"})

8. Run raw SQL queries

# Insert
db.query("INSERT INTO users (name, email) VALUES (%s, %s)", ("John", "john@example.com"))

# Select
result = db.query("SELECT * FROM users WHERE name = %s", ("John",))






