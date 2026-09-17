from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "darul_bahs.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return "Darul Bahs Wal Ifta - API yana aiki!"


@app.route("/teachers", methods=["GET"])
def get_teachers():
    conn = get_db()
    teachers = conn.execute("SELECT * FROM teachers").fetchall()
    conn.close()
    return jsonify([dict(teacher) for teacher in teachers])


@app.route("/teachers", methods=["POST"])
def add_teacher():
    data = request.get_json() or {}

    name = data.get("name")
    specialization = data.get("specialization")
    bio = data.get("bio")

    conn = get_db()
    conn.execute(
        "INSERT INTO teachers (name, specialization, bio) VALUES (?, ?, ?)",
        (name, specialization, bio)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "An kara malami successfully!"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
