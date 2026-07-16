import os
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app import db
from app.models import Job, Recruiter, Application, Resume, Applicant

recruiter_dashboard_bp = Blueprint('recruiter_dashboard', __name__)

@recruiter_dashboard_bp.route('/<recruiter_id>/dashboard', methods=['GET'])
@jwt_required()
def get_recruiter_dashboard(recruiter_id):
    jwt_user_id = get_jwt_identity()
    if str(jwt_user_id) != str(recruiter_id):
        return jsonify({"error": "Unauthorized"}), 403

    recruiter = Recruiter.query.get(recruiter_id)
    if not recruiter:
        return jsonify({"error": "Recruiter not found"}), 404

    # 1. Active job postings (status = 'published')
    jobs = Job.query.filter_by(recruiter_id=recruiter_id).order_by(Job.created_at.desc()).all()
    active_postings = sum(1 for job in jobs if job.status == 'published')

    # 2. Total unique candidates who applied to recruiter's jobs
    job_ids = [job.job_id for job in jobs]
    if job_ids:
        applications = Application.query.filter(Application.job_id.in_(job_ids)).all()
    else:
        applications = []

    unique_candidate_ids = {app.applicant_id for app in applications}
    total_candidates = len(unique_candidate_ids)

    # 3. Calculate candidate details and matching scores
    candidate_matches = []
    top_match_score = 0

    # Build job lookup for quick access
    job_lookup = {job.job_id: job for job in jobs}

    for app in applications:
        job = job_lookup.get(app.job_id)
        if not job:
            continue

        applicant = Applicant.query.get(app.applicant_id)
        resume = Resume.query.get(app.resume_id) if app.resume_id else None
        if not resume:
            resume = Resume.query.filter_by(applicant_id=app.applicant_id).order_by(Resume.uploaded_at.desc()).first()

        applicant_name = (applicant.name or (resume.name if resume else None) or "Unknown Candidate")
        job_title = job.title
        resume_skills = resume.skills if (resume and resume.skills) else []
        resume_file_path = os.path.basename(resume.file_path) if resume and resume.file_path else ""

        # Match score calculation
        job_skills = set(s.lower() for s in (job.skills or []))
        candidate_skills = set(s.lower() for s in resume_skills)
        matched = job_skills & candidate_skills
        matching_score = round((len(matched) / len(job_skills) * 100) if job_skills else 0)

        if matching_score > top_match_score:
            top_match_score = matching_score

        candidate_matches.append({
            "applicant_id": str(app.applicant_id),
            "applicant_name": applicant_name,
            "job_title": job_title,
            "matching_score": matching_score,
            "resume_skills": resume_skills[:3],  # Limit to top 3 skills to keep it neat
            "resume_file_path": resume_file_path,
        })

    # Sort matches by score descending
    candidate_matches.sort(key=lambda x: x["matching_score"], reverse=True)
    top_candidates = candidate_matches[:5]  # Get top 5

    # 4. Active jobs for the jobs table
    job_list = []
    for job in jobs:
        # Count applications for this specific job
        job_apps_count = sum(1 for app in applications if app.job_id == job.job_id)
        job_list.append({
            "job_id": str(job.job_id),
            "title": job.title,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "candidates_count": job_apps_count
        })

    return jsonify({
        "name": recruiter.name or "Recruiter",
        "active_postings": active_postings,
        "total_candidates": total_candidates,
        "top_match_score": top_match_score,
        "top_candidates": top_candidates,
        "jobs": job_list
    }), 200
