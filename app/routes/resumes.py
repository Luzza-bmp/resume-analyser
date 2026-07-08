import os
import uuid
from flask import Blueprint, request, jsonify
from app import db
from app.models import Resume
from app.services.resume_parser import parse_resume

resumes_bp = Blueprint("resumes", __name__)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@resumes_bp.route("", methods=["GET"])
def get_resumes():
    """GET /api/resumes?applicant_id=<uuid>
    Returns all resumes for the given applicant, newest first."""
    applicant_id = request.args.get("applicant_id")
    if not applicant_id:
        return jsonify({"error": "applicant_id is required"}), 400

    try:
        resumes = (
            Resume.query
            .filter_by(applicant_id=applicant_id)
            .order_by(Resume.uploaded_at.desc())
            .all()
        )
        result = []
        for r in resumes:
            result.append({
                "resume_id": str(r.resume_id),
                "applicant_id": str(r.applicant_id),
                "file_path": os.path.basename(r.file_path) if r.file_path else "",
                "name": r.name or "",
                "email": r.email or "",
                "phone": r.phone or "",
                "experience_years": float(r.experience_years) if r.experience_years else 0,
                "skills": r.skills or [],
                "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else "",
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@resumes_bp.route("/upload-pdf", methods=["POST"])
def upload_pdf():
    """POST /api/resumes/upload-pdf
    Accepts multipart/form-data with 'file' (PDF) and 'applicant_id'.
    Parses the resume, extracts skills, saves to DB, returns result."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    applicant_id = request.form.get("applicant_id")

    if not applicant_id:
        return jsonify({"error": "applicant_id is required"}), 400

    if not file.filename:
        return jsonify({"error": "Empty file name"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400

    # Save the uploaded file with a unique name
    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(filepath)

    # Parse the resume
    try:
        parsed_data = parse_resume(filepath)
    except Exception as e:
        return jsonify({"error": f"Failed to parse resume: {str(e)}"}), 500

    if "error" in parsed_data:
        return jsonify(parsed_data), 400

    skills = parsed_data.get("skills", [])

    # Save the resume record in DB
    resume = Resume(
        applicant_id=applicant_id,
        file_path=filepath,
        raw_text=str(parsed_data),
        name=parsed_data.get("name"),
        email=parsed_data.get("email"),
        phone=parsed_data.get("phone"),
        experience_years=parsed_data.get("experience"),
        skills=skills,
    )
    db.session.add(resume)
    db.session.commit()

    return jsonify({
        "resume_id": str(resume.resume_id),
        "applicant_id": str(resume.applicant_id),
        "file_path": os.path.basename(filepath),
        "name": resume.name or "",
        "email": resume.email or "",
        "phone": resume.phone or "",
        "experience_years": float(resume.experience_years) if resume.experience_years else 0,
        "skills": skills,
        "skill_count": len(skills),
        "uploaded_at": resume.uploaded_at.isoformat() if resume.uploaded_at else "",
    }), 201


@resumes_bp.route("/download/<filename>", methods=["GET"])
def download_resume(filename):
    """Serve resume files stored on disk."""
    import os
    from flask import send_from_directory
    return send_from_directory(os.path.abspath(UPLOAD_FOLDER), filename)

