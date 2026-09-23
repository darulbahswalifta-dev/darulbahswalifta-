from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "darul-bahs-wal-ifta-dev-secret-2026")
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024


STORAGE_DIR = os.environ.get("STORAGE_DIR", os.path.join(app.root_path, "storage"))
DATABASE = os.path.join(STORAGE_DIR, "darul_bahs.db")
PDF_FOLDER = os.path.join(STORAGE_DIR, "pdfs")
EPUB_FOLDER = os.path.join(STORAGE_DIR, "epubs")
AUDIO_FOLDER = os.path.join(STORAGE_DIR, "audios")
VIDEO_FOLDER = os.path.join(STORAGE_DIR, "videos")
for folder in (STORAGE_DIR, PDF_FOLDER, EPUB_FOLDER, AUDIO_FOLDER, VIDEO_FOLDER):
    os.makedirs(folder, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT,
            bio TEXT,
            username TEXT,
            password_hash TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            description TEXT,
            file_path TEXT,
            file_type TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT,
            teacher_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            description TEXT,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            category TEXT DEFAULT 'Books'
        )
    """)

    media_columns = [row[1] for row in conn.execute("PRAGMA table_info(media)").fetchall()]
    if "category" not in media_columns:
        conn.execute("ALTER TABLE media ADD COLUMN category TEXT DEFAULT 'Books'")

    if conn.execute("SELECT COUNT(*) FROM teachers").fetchone()[0] == 0:
        teachers_seed = [
            ("Malam Muhammad", "Fiqh", "Malami mai koyar da ilimin Fiqhu"),
            ("Malam Abdullahi", "Hadith", "Malami mai koyar da ilimin Hadisi"),
            ("Malam Gwaji", "Fiqh", "Malami mai koyar da ilimin Fiqhu"),
            ("Shaikh Ahmad Salihu Bukar", "Akida", "Malami Mai Kwarewa a fannin Akida"),
            ("Shaikh Abubakar Muhammad Musa", "Fiqhu and Lugga", "Shaikh limami ne na Ahlussunnah a Ningi kuma Shugaban Mallamai na Ningi Iga")
        ]
        conn.executemany("INSERT INTO teachers (name, specialization, bio) VALUES (?, ?, ?)", teachers_seed)

    columns = [row["name"] for row in conn.execute("PRAGMA table_info(media)").fetchall()]
    if "category" not in columns:
        conn.execute("ALTER TABLE media ADD COLUMN category TEXT DEFAULT 'Books'")
        conn.commit()

    media_seed = [
        ("Ethics of Islam", "", "Islamic Research", "pdfs/Ethics_of_Islam.pdf", "PDF", "Books"),
        ("His ah principle in Islam", "", "Islamic Research", "pdfs/His_ah principle in Islam.pdf", "PDF", "Books"),
        ("Noor Book", "", "Islamic Research", "pdfs/Noor-Book.com_.pdf", "PDF", "Books"),
        ("Book 1", "", "Islamic Research", "pdfs/book1.pdf", "PDF", "Books"),
        ("La ilaha Illallah", "", "Islamic Research", "pdfs/pdf_6c3fc0c983de44a1907ff0c2bf966c4.pdf", "PDF", "Aqida")
    ]

    for item in media_seed:
        if not conn.execute("SELECT 1 FROM media WHERE title = ?", (item[0],)).fetchone():
            conn.execute(
                "INSERT INTO media (title, author, description, file_path, file_type, category) VALUES (?, ?, ?, ?, ?, ?)",
                item
            )
    admin_username = os.environ.get("ADMIN_USERNAME")
    admin_password = os.environ.get("ADMIN_PASSWORD")

    if admin_username and admin_password:
        admin_hash = generate_password_hash(admin_password)
        existing_admin = conn.execute(
            "SELECT id FROM admins WHERE username = ?",
            (admin_username,)
        ).fetchone()

        if existing_admin:
            conn.execute(
                "UPDATE admins SET password_hash = ? WHERE username = ?",
                (admin_hash, admin_username)
            )
        else:
            conn.execute(
                "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                (admin_username, admin_hash)
            )

    conn.commit()
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
    return render_template("questions.html", questions=[dict(row) for row in rows])

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
    return send_from_directory(PDF_FOLDER, filename, as_attachment=True)
@app.route("/study1")
def study1():
    return render_template("study1.html")

@app.route("/study2")
def study2():
    return render_template("study2.html")

@app.route("/download-media/<int:media_id>")
def download_media(media_id):
    conn = get_db()
    item = conn.execute("SELECT * FROM media WHERE id = ?", (media_id,)).fetchone()
    conn.close()
    if not item:
        return "Content not found", 404
    file_path = item["file_path"]
    return send_from_directory(app.static_folder, file_path, as_attachment=True)

@app.route("/studies")
def studies():
    conn = get_db()
    studies = conn.execute("SELECT * FROM media WHERE file_type = 'PDF' ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("studies.html", studies=studies)

@app.route("/study3")
def study3():
    return render_template("study3.html")

@app.route("/download/book1")
def download_book1():
    return send_from_directory(PDF_FOLDER, "book1.pdf", as_attachment=True)

@app.route("/downloads")
def downloads():
    return render_template("downloads.html")

@app.route("/scholar-login", methods=["GET", "POST"])
def scholar_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = get_db()
        teacher = conn.execute("SELECT * FROM teachers WHERE username = ?", (username,)).fetchone()
        conn.close()
        if teacher and check_password_hash(teacher["password_hash"], password):
            session["teacher_id"] = teacher["id"]
            session["teacher_name"] = teacher["name"]
            return redirect(url_for("scholar_dashboard"))
        return render_template("scholar_login.html", error="Username ko password ba daidai ba")
    return render_template("scholar_login.html")

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_db()
        admin = conn.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        conn.close()
        if admin and check_password_hash(admin["password_hash"], password):
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            return redirect(url_for("admin_dashboard"))
        return render_template("admin_login.html", error="Username ko password ba daidai ba")
    return render_template("admin_login.html")


@app.route("/scholar-dashboard")
def scholar_dashboard():
    if "teacher_id" not in session:
        return redirect(url_for("scholar_login"))
    return render_template("scholar_dashboard.html", name=session.get("teacher_name"))



@app.route("/scholar-logout")
def scholar_logout():
    session.pop("teacher_id", None)
    session.pop("teacher_name", None)
    return redirect(url_for("scholar_login"))

@app.route("/answer-question/<int:question_id>", methods=["POST"])
def answer_question(question_id):
    if "teacher_id" not in session:
        return redirect(url_for("scholar_login"))

    answer = request.form.get("answer", "").strip()

    if not answer:
        return "Answer cannot be empty", 400

    conn = get_db()
    conn.execute(
        "UPDATE questions SET answer = ? WHERE id = ?",
        (answer, question_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("get_questions"))


@app.route("/admin-add-teacher", methods=["GET", "POST"])
def admin_add_teacher():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        specialization = request.form.get("specialization", "").strip()
        bio = request.form.get("bio", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not name or not username or not password:
            return render_template("admin_add_teacher.html", error="Name, username and password are required.")

        password_hash = generate_password_hash(password)

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO teachers (name, specialization, bio, username, password_hash) VALUES (?, ?, ?, ?, ?)",
                (name, specialization, bio, username, password_hash)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("admin_add_teacher.html", error="Username already exists.")
        conn.close()

        return redirect(url_for("get_teachers"))

    return render_template("admin_add_teacher.html")
@app.route("/admin-teachers")
def admin_teachers():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()
    teachers = conn.execute("SELECT * FROM teachers ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("admin_teachers.html", teachers=[dict(t) for t in teachers])

@app.route("/admin-dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()
    teachers_count = conn.execute("SELECT COUNT(*) FROM teachers").fetchone()[0]
    questions_count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    studies_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    pdf_count = conn.execute("SELECT COUNT(*) FROM media WHERE file_type = 'PDF'").fetchone()[0]
    epub_count = conn.execute("SELECT COUNT(*) FROM media WHERE file_type = 'EPUB'").fetchone()[0]
    audio_count = conn.execute("SELECT COUNT(*) FROM media WHERE file_type = 'Audio'").fetchone()[0]
    video_count = conn.execute("SELECT COUNT(*) FROM media WHERE file_type = 'Video'").fetchone()[0]
    recent_questions = conn.execute("SELECT * FROM questions ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        teachers_count=teachers_count,
        questions_count=questions_count,
        studies_count=studies_count,
        pdf_count=pdf_count,
        epub_count=epub_count,
        audio_count=audio_count,
        video_count=video_count,
        recent_questions=recent_questions
    )


@app.route("/admin-manage-content")
def admin_manage_content():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()
    media = conn.execute(
        "SELECT * FROM media ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template(
        "admin_manage_content.html",
        media=media
    )

@app.route("/admin-delete-content/<int:content_id>", methods=["POST"])
def admin_delete_content(content_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()
    item = conn.execute(
        "SELECT file_path FROM media WHERE id = ?",
        (content_id,)
    ).fetchone()

    if not item:
        conn.close()
        return "Content not found", 404

    file_path = item["file_path"]
    full_path = os.path.abspath(os.path.join(app.static_folder, file_path))
    static_path = os.path.abspath(app.static_folder)

    if os.path.commonpath([full_path, static_path]) != static_path:
        conn.close()
        return "Invalid file path", 400

    try:
        if os.path.isfile(full_path):
            os.remove(full_path)
    except OSError:
        conn.close()
        return "Could not delete the file", 500

    conn.execute("DELETE FROM media WHERE id = ?", (content_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_manage_content"))

@app.route("/admin-edit-content/<int:content_id>", methods=["GET", "POST"])
def admin_edit_content(content_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()
    item = conn.execute(
        "SELECT * FROM media WHERE id = ?",
        (content_id,)
    ).fetchone()

    if not item:
        conn.close()
        return "Content not found", 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            conn.close()
            return render_template(
                "admin_edit_content.html",
                item=item,
                error="Title is required."
            )

        conn.execute(
            "UPDATE media SET title = ?, author = ?, description = ? WHERE id = ?",
            (title, author, description, content_id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("admin_manage_content"))

    conn.close()
    return render_template("admin_edit_content.html", item=item)

@app.route("/admin-logout")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("admin_username", None)
    return redirect(url_for("admin_login"))


@app.route("/audios")
def audios():
    return render_template("audios.html")

@app.route("/videos")
def videos():
    return render_template("videos.html")


@app.route("/download-audio/<path:filename>")
def download_audio(filename):
    return send_from_directory("static/audio", filename, as_attachment=True)


@app.route("/download-video/<path:filename>")
def download_video(filename):
    return send_from_directory("static/videos", filename, as_attachment=True)


@app.route("/admin-add-pdf", methods=["GET", "POST"])
def admin_add_pdf():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        description = request.form.get("description", "").strip()
        file = request.files.get("file")

        if not title or not file or not file.filename:
            return render_template(
                "admin_add_pdf.html",
                error="Please provide a title and select a PDF file."
            )

        original_filename = file.filename or ""

        if not original_filename.lower().endswith(".pdf"):
            return render_template(
                "admin_add_pdf.html",
                error="Only PDF files are allowed."
            )

        filename = secure_filename(original_filename)

        if not filename or not filename.lower().endswith(".pdf"):
            import uuid
            filename = f"pdf_{uuid.uuid4().hex}.pdf"

        pdf_folder = PDF_FOLDER
        os.makedirs(pdf_folder, exist_ok=True)

        file.save(os.path.join(pdf_folder, filename))

        conn = get_db()
        category = request.form.get("category", "Books").strip()

        conn.execute(
            "INSERT INTO media (title, author, description, file_path, file_type, category) VALUES (?, ?, ?, ?, ?, ?)",
            (title, author, description, f"pdfs/{filename}", "PDF", category)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("admin_dashboard"))

    return render_template("admin_add_pdf.html")




@app.route("/admin-add-audio", methods=["GET", "POST"])
def admin_add_audio():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        description = request.form.get("description", "").strip()
        file = request.files.get("file")

        if not title or not file or not file.filename:
            return render_template(
                "admin_add_audio.html",
                error="Please provide a title and select an audio file."
            )

        filename = secure_filename(file.filename)
        allowed = {".mp3", ".m4a", ".wav", ".ogg", ".aac"}

        if not any(filename.lower().endswith(ext) for ext in allowed):
            return render_template(
                "admin_add_audio.html",
                error="Only supported audio files are allowed."
            )

        audio_folder = AUDIO_FOLDER
        os.makedirs(audio_folder, exist_ok=True)

        file.save(os.path.join(audio_folder, filename))

        conn = get_db()
        conn.execute(
            "INSERT INTO media (title, author, description, file_path, file_type) VALUES (?, ?, ?, ?, ?)",
            (title, author, description, f"audios/{filename}", "Audio")
        )
        conn.commit()
        conn.close()

        return redirect(url_for("admin_dashboard"))

    return render_template("admin_add_audio.html")



@app.route("/admin-add-video", methods=["GET", "POST"])
def admin_add_video():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        description = request.form.get("description", "").strip()
        file = request.files.get("file")

        if not title or not file or not file.filename:
            return render_template(
                "admin_add_video.html",
                error="Please provide a title and select a video file."
            )

        filename = secure_filename(file.filename)
        allowed = {".mp4", ".webm", ".mov", ".mkv"}

        if Path(filename).suffix.lower() not in allowed:
            return render_template(
                "admin_add_video.html",
                error="Only supported video files are allowed."
            )

        video_folder = VIDEO_FOLDER
        os.makedirs(video_folder, exist_ok=True)

        file.save(os.path.join(video_folder, filename))

        return redirect(url_for("admin_dashboard"))

    return render_template("admin_add_video.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)

