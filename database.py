import sqlite3

DATABASE = "darul_bahs.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS teachers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, specialization TEXT, bio TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, author TEXT, description TEXT, file_path TEXT, file_type TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, question TEXT NOT NULL, answer TEXT, teacher_id INTEGER, FOREIGN KEY (teacher_id) REFERENCES teachers(id))")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database ta kammala!")
