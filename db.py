import pymysql
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

def connect():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def add_task(title, description, priority):
    with connect() as conn:
        with conn.cursor() as cursor:
            sql = "INSERT INTO tasks (title, description, priority) VALUES (%s, %s, %s)"
            cursor.execute(sql, (title, description, priority))
        conn.commit()

def get_tasks():
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            return cursor.fetchall()
def update_task(task_id, title, description, priority):
    with connect() as conn:
        with conn.cursor() as cursor:
            sql = "UPDATE tasks SET title=%s, description=%s, priority=%s WHERE id=%s"
            cursor.execute(sql, (title, description, priority, task_id))
        conn.commit()

def delete_task(task_id):
    with connect() as conn:
        with conn.cursor() as cursor:
            sql = "DELETE FROM tasks WHERE id=%s"
            cursor.execute(sql, (task_id,))
        conn.commit()

def get_task_by_id(task_id):
    with connect() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM tasks WHERE id=%s"
            cursor.execute(sql, (task_id,))
            return cursor.fetchone()
