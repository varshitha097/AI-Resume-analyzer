
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, Response
from werkzeug.utils import secure_filename
from src.pipeline import ResumeAnalyzer
from src.report import results_to_csv

BASE_DIR = Path(__file__).parent.resolve()
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}

app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024

analyzer = ResumeAnalyzer()
LAST_RESULTS = []


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "engine": analyzer.similarity_engine.backend})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    global LAST_RESULTS
    jd_text = request.form.get("jd_text", "").strip()
    jd_file = request.files.get("jd_file")

    if jd_file and jd_file.filename:
        jd_name = secure_filename(jd_file.filename)
        jd_path = UPLOAD_DIR / jd_name
        jd_file.save(jd_path)
        from src.parser import extract_text_from_file
        jd_text, _ = extract_text_from_file(str(jd_path))

    if not jd_text:
        return jsonify({"error": "Please paste a job description or upload a JD file."}), 400

    files = request.files.getlist("resumes")
    if not files:
        return jsonify({"error": "Please upload at least one resume PDF/TXT/DOCX."}), 400

    saved_paths = []
    for f in files:
        if not f.filename:
            continue
        if not allowed_file(f.filename):
            return jsonify({"error": f"Unsupported file type: {f.filename}. Use PDF, TXT or DOCX."}), 400
        filename = secure_filename(f.filename)
        path = UPLOAD_DIR / filename
        f.save(path)
        saved_paths.append(path)

    if not saved_paths:
        return jsonify({"error": "No valid resume files uploaded."}), 400

    output = analyzer.analyze_many(saved_paths, jd_text)
    LAST_RESULTS = output["ranking"]
    return jsonify(output)


@app.route("/api/export.csv")
def export_csv():
    csv_text = results_to_csv(LAST_RESULTS)
    return Response(
        csv_text,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=resume_ranking_report.csv"},
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
