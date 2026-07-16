from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app import db
from app.models import Resume, Analysis

# Blueprint for applicant dashboard related endpoints
dashboard_bp = Blueprint('applicant_dashboard', __name__)

@dashboard_bp.route('/<applicant_id>/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard(applicant_id):
    """Return dashboard metrics for the given applicant.
    Expected fields for the frontend:
    - has_resume (bool)
    - resume_strength (overall_score of latest analysis or 0)
    - avg_match_score (average of all match scores for applicant)
    - skill_count (number of skills extracted from latest resume)
    - missing_skills (list from latest analysis)
    - resume_filename (original filename)
    - resume_uploaded_at (ISO timestamp)
    - recent_jobs (placeholder list)
    - top_jobs (placeholder list)
    """
    # Verify JWT identity matches the applicant or has appropriate permissions.
    # For simplicity, we assume the JWT identity is the applicant's user_id.
    jwt_user_id = get_jwt_identity()
    if str(jwt_user_id) != str(applicant_id):
        # In a real app you'd check admin rights; here we just restrict.
        return jsonify({"error": "Unauthorized"}), 403

    # Check if applicant has any resume uploaded.
    resume = (
        Resume.query
        .filter_by(applicant_id=applicant_id)
        .order_by(Resume.uploaded_at.desc())
        .first()
    )
    has_resume = bool(resume)

    if not has_resume:
        return jsonify({
            "has_resume": False,
            "resume_strength": 0,
            "avg_match_score": 0,
            "skill_count": 0,
            "missing_skills": [],
            "resume_filename": None,
            "resume_uploaded_at": None,
            "recent_jobs": [],
            "top_jobs": [],
        })

    # Latest analysis for this resume (if any)
    latest_analysis = (
        Analysis.query
        .filter_by(resume_id=resume.resume_id)
        .order_by(Analysis.analyzed_at.desc())
        .first()
    )

    # Average match score across all analyses for this applicant
    avg_match = (
        db.session.query(func.avg(Analysis.match_score))
        .join(Resume, Analysis.resume_id == Resume.resume_id)
        .filter(Resume.applicant_id == applicant_id)
        .scalar()
    ) or 0
    avg_match = round(float(avg_match), 2)

    # Add job listings for applicant view
    from app.models import Job
    # Recent jobs: latest 4 published jobs
    recent_jobs_q = Job.query.filter_by(status='published').order_by(Job.created_at.desc()).limit(4).all()
    recent_jobs = []
    for job in recent_jobs_q:
        recent_jobs.append({
            "job_id": str(job.job_id),
            "title": job.title,
            "description": job.description,
            "skills": job.skills,
            "experience_level": job.experience_level,
            "job_type": job.job_type,
            "location": job.location,
            "salary_min": float(job.salary_min) if job.salary_min is not None else None,
            "salary_max": float(job.salary_max) if job.salary_max is not None else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        })
    # Top jobs could be same as recent for now
    top_jobs = recent_jobs
    response = {
        "has_resume": True,
        "resume_strength": latest_analysis.overall_score if latest_analysis else 0,
        "avg_match_score": avg_match,
        "skill_count": len(resume.skills) if resume.skills else 0,
        "missing_skills": latest_analysis.missing_skills if latest_analysis else [],
        "resume_filename": resume.file_path.split('/')[-1] if resume.file_path else None,
        "resume_uploaded_at": resume.uploaded_at.isoformat() if resume.uploaded_at else None,
        "recent_jobs": recent_jobs,
        "top_jobs": top_jobs,
    }
    return jsonify(response)


@dashboard_bp.route('/<applicant_id>/matched-jobs', methods=['GET'])
@jwt_required()
def get_matched_jobs(applicant_id):
    jwt_user_id = get_jwt_identity()
    if str(jwt_user_id) != str(applicant_id):
        return jsonify({"error": "Unauthorized"}), 403

    resume = (
        Resume.query
        .filter_by(applicant_id=applicant_id)
        .order_by(Resume.uploaded_at.desc())
        .first()
    )

    from app.models import Job, Recruiter
    jobs = Job.query.filter_by(status='published').all()

    matched_list = []
    resume_skills = set(s.lower() for s in (resume.skills or [])) if resume else set()

    for job in jobs:
        recruiter = Recruiter.query.get(job.recruiter_id)
        job_skills = set(s.lower() for s in (job.skills or []))
        overlap = resume_skills & job_skills if resume else set()
        match_score = round(len(overlap) / len(job_skills) * 100) if job_skills and resume else 0

        matched_list.append({
            "job_id": str(job.job_id),
            "title": job.title,
            "description": job.description,
            "skills": job.skills or [],
            "experience_level": job.experience_level,
            "job_type": job.job_type,
            "location": job.location,
            "salary_min": float(job.salary_min) if job.salary_min is not None else None,
            "salary_max": float(job.salary_max) if job.salary_max is not None else None,
            "recruiter_company": recruiter.company if recruiter else None,
            "recruiter_name": recruiter.name if recruiter else None,
            "matching_score": match_score,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        })

    # Sort by matching_score descending
    matched_list.sort(key=lambda x: x["matching_score"], reverse=True)

    return jsonify({
        "resume_id": str(resume.resume_id) if resume else None,
        "matched_jobs": matched_list
    }), 200


@dashboard_bp.route('/<applicant_id>/applications', methods=['GET'])
@jwt_required()
def get_applicant_applications(applicant_id):
    jwt_user_id = get_jwt_identity()
    if str(jwt_user_id) != str(applicant_id):
        return jsonify({"error": "Unauthorized"}), 403

    from app.models import Application, Job, Recruiter

    apps = Application.query.filter_by(applicant_id=applicant_id).all()
    applied_job_ids = [str(a.job_id) for a in apps]
    applications = []

    for app in apps:
        job = Job.query.get(app.job_id)
        recruiter = Recruiter.query.get(job.recruiter_id) if job else None
        applications.append({
            "application_id": str(app.application_id),
            "job_id": str(app.job_id),
            "job_title": job.title if job else "Unknown job",
            "company": recruiter.company if recruiter and recruiter.company else "Recruiter",
            "status": app.status or "applied",
            "applied_at": app.applied_at.isoformat() if app.applied_at else "",
        })

    return jsonify({"applied_job_ids": applied_job_ids, "applications": applications}), 200


@dashboard_bp.route('/<applicant_id>/skill-gap', methods=['GET'])
@jwt_required()
def get_skill_gap(applicant_id):
    """GET /api/applicants/<applicant_id>/skill-gap?job_id=<optional>
    Returns a skill gap analysis comparing the applicant's resume skills
    against the skills required for a specific job (or across all jobs).
    """
    from flask import request
    from app.models import Job, Recruiter

    jwt_user_id = get_jwt_identity()
    if str(jwt_user_id) != str(applicant_id):
        return jsonify({"error": "Unauthorized"}), 403

    # Get applicant's latest resume
    resume = (
        Resume.query
        .filter_by(applicant_id=applicant_id)
        .order_by(Resume.uploaded_at.desc())
        .first()
    )
    if not resume:
        return jsonify({"error": "No resume found. Please upload your resume first."}), 404

    resume_skills = set(s.lower().strip() for s in (resume.skills or []))

    job_id = request.args.get("job_id")

    if job_id:
        # Analyze against a specific job
        job = Job.query.get(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404

        recruiter = Recruiter.query.get(job.recruiter_id)
        job_skills = set(s.lower().strip() for s in (job.skills or []))

        matched = sorted(resume_skills & job_skills)
        missing_raw = sorted(job_skills - resume_skills)

        # Assign priority: skills that appear first in the job's list = higher priority
        job_skills_ordered = [s.lower().strip() for s in (job.skills or [])]
        def priority(skill):
            try:
                idx = job_skills_ordered.index(skill)
                if idx < len(job_skills_ordered) // 3:
                    return "High"
                elif idx < 2 * len(job_skills_ordered) // 3:
                    return "Medium"
            except ValueError:
                pass
            return "Low"

        missing_skills = [{"skill": s, "priority": priority(s)} for s in missing_raw]
        readiness_score = round((len(matched) / len(job_skills)) * 100) if job_skills else 100

        return jsonify({
            "job_id": str(job.job_id),
            "job_title": job.title,
            "company": recruiter.company if recruiter else None,
            "resume_skills": sorted(resume_skills),
            "matched_skills": matched,
            "missing_skills": missing_skills,
            "readiness_score": readiness_score,
        }), 200

    else:
        # Aggregate across ALL published jobs — find most-demanded missing skills
        jobs = Job.query.filter_by(status='published').all()
        if not jobs:
            return jsonify({
                "job_title": "All Jobs",
                "resume_skills": sorted(resume_skills),
                "matched_skills": [],
                "missing_skills": [],
                "readiness_score": 100,
            }), 200

        skill_demand: dict = {}  # skill -> count of jobs requiring it
        matched_across: set = set()

        for job in jobs:
            job_skills = set(s.lower().strip() for s in (job.skills or []))
            matched_across |= resume_skills & job_skills
            for skill in job_skills - resume_skills:
                skill_demand[skill] = skill_demand.get(skill, 0) + 1

        # Sort missing skills by how many jobs demand them (most demanded = High priority)
        sorted_missing = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)
        total_jobs = len(jobs)

        def agg_priority(count):
            if count >= total_jobs * 0.6:
                return "High"
            elif count >= total_jobs * 0.3:
                return "Medium"
            return "Low"

        missing_skills = [{"skill": s, "priority": agg_priority(c)} for s, c in sorted_missing]

        # Readiness = percentage of jobs where applicant has ≥1 matching skill
        jobs_with_match = sum(
            1 for job in jobs
            if resume_skills & set(s.lower().strip() for s in (job.skills or []))
        )
        readiness_score = round((jobs_with_match / total_jobs) * 100) if total_jobs else 100

        return jsonify({
            "job_title": "All Jobs",
            "resume_skills": sorted(resume_skills),
            "matched_skills": sorted(matched_across),
            "missing_skills": missing_skills,
            "readiness_score": readiness_score,
        }), 200



