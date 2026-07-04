from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

from app.services.resume_parser import parse_resume
from app.services.skill_matcher import extract_skills
from app.utils.scorer import calculate_match_score, score_format, overall_score
from app.utils.feedback import generate_feedback
from app.repositories.applicant_repository import save_resume, save_analysis

applicant_bp = Blueprint("applicant", __name__)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@applicant_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload():
    applicant_id = get_jwt_identity()
    file = request.files['resume']
    jd_text = request.form['jd_text']

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    parsed_data = parse_resume(filepath)
    if "error" in parsed_data:
        return jsonify(parsed_data), 400

    resume = save_resume(applicant_id, filepath, str(parsed_data), parsed_data)

    resume_skills = parsed_data.get("skills", [])
    jd_skills = extract_skills(jd_text)

    matched = sorted(list(set(resume_skills) & set(jd_skills)))
    missing = sorted(list(set(jd_skills) - set(resume_skills)))

    match_score = calculate_match_score(resume_skills, jd_skills)
    fmt_score = score_format(parsed_data)
    overall = overall_score(match_score, fmt_score)
    suggestions = generate_feedback(missing, overall)

    analysis = save_analysis(
        resume.resume_id, jd_text, match_score, fmt_score, overall,
        matched, missing, suggestions
    )

    return jsonify({
        "resume_id": str(resume.resume_id),
        "analysis_id": str(analysis.analysis_id),
        "match_score": match_score,
        "format_score": fmt_score,
        "overall_score": overall,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggestions": suggestions
    }), 201