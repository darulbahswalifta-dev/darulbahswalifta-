from flask import Flask, request, jsonify, render_template, send_from_directory
import sqlite3

app = Flask(__name__)

DATABASE = "darul_bahs.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():



           return render_template("index.html")

@app.route("/teachers", methods=["GET"])
def get_teachers():
    conn = get_db()
    teachers = conn.execute("SELECT * FROM teachers").fetchall()
    conn.close()
    return render_template("teachers.html", teachers=[dict(teacher) for teacher in teachers])


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


@app.route("/questions", methods=["GET"])
def get_questions():
    conn = get_db()
    rows = conn.execute("SELECT id, name, question, answer, teacher_id FROM questions ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/questions", methods=["POST"])
def add_question():
    data = request.get_json() or {}
    name = data.get("name")
    question = data.get("question")
    answer = data.get("answer", "")
    teacher_id = data.get("teacher_id")
    if not name or not question:
        return jsonify({"error": "name da question suna da muhimmanci"}), 400
    conn = get_db()
    conn.execute("INSERT INTO questions (name, question, answer, teacher_id) VALUES (?, ?, ?, ?)", (name, question, answer, teacher_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "An karbi tambayar cikin nasara!"}), 201

@app.route("/ask")
def ask():
         return render_template("ask.html")


@app.route("/download-pdf")
def download_pdf():
    filename = request.args.get("file")
    allowed = ["His ah principle in Islam.pdf", "Ethics_of_Islam.pdf", "book1.pdf"]
    if filename not in allowed:
        return "PDF ba a samu ba", 404
    return send_from_directory("static/pdfs", filename, as_attachment=True)
@app.route("/study1")
def study1():
    return render_template("study1.html")

@app.route("/study2")
def study2():
    return render_template("study2.html")

@app.route("/studies")
def studies():
    return render_template("studies.html")

@app.route("/study3")
def study3():
    return render_template("study3.html")

@app.route("/download/book1")
def download_book1():
    return send_from_directory("static/pdfs", "book1.pdf", as_attachment=True)

@app.route("/downloads")
def downloads():
    return render_template("downloads.html")

if __name__ == "__main__":
          app.run(host="0.0.0.0", port=5000, debug=True)
@app.route("/study3")
def study3():
    return render_template("study3.html")


