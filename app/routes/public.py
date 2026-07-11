from flask import Blueprint, jsonify
from app import db
from app.models import Job, Recruiter, Applicant, Resume, Application

public_bp = Blueprint('public', __name__)

@public_bp.route('/preview', methods=['GET'])
def get_public_preview():
    # 1. Stats
    jobs_count = Job.query.count()
    recruiters_count = Recruiter.query.count()
    applicants_count = Applicant.query.count()
    resumes_count = Resume.query.count()

    # 2. Recent Jobs
    recent_jobs_q = Job.query.filter_by(status='published').order_by(Job.created_at.desc()).limit(5).all()
    recent_jobs = []
    for job in recent_jobs_q:
        rec = Recruiter.query.get(job.recruiter_id)
        recent_jobs.append({
            "job_id": str(job.job_id),
            "title": job.title,
            "recruiter_company": rec.company if rec else "",
            "recruiter_name": rec.name if rec else "Recruiter",
            "location": job.location or "",
            "skills": job.skills or [],
        })

    # 3. Top Ranked Candidates (derived from applications)
    apps = Application.query.all()
    candidates = []
    for app in apps:
        job = Job.query.get(app.job_id)
        applicant = Applicant.query.get(app.applicant_id)
        resume = Resume.query.get(app.resume_id) if app.resume_id else None
        if not resume:
            resume = Resume.query.filter_by(applicant_id=app.applicant_id).order_by(Resume.uploaded_at.desc()).first()

        if not job or not applicant:
            continue

        job_skills = set(s.lower() for s in (job.skills or []))
        candidate_skills = set(s.lower() for s in (resume.skills or [] if resume else []))
        matched = job_skills & candidate_skills
        score = round((len(matched) / len(job_skills) * 100) if job_skills else 0)

        candidates.append({
            "ranking_id": str(app.application_id),
            "applicant_name": applicant.name or (resume.name if resume else "Candidate"),
            "job_title": job.title,
            "matching_score": score,
            "resume_skills": resume.skills if (resume and resume.skills) else [],
        })

    # Sort candidates by match score descending
    candidates.sort(key=lambda x: x["matching_score"], reverse=True)
    top_candidates = candidates[:5]

    return jsonify({
        "stats": {
            "jobs": jobs_count,
            "recruiters": recruiters_count,
            "applicants": applicants_count,
            "resumes": resumes_count
        },
        "recent_jobs": recent_jobs,
        "top_candidates": top_candidates
    }), 200
