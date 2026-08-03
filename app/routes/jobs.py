from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Job, Recruiter, Application, Resume, Applicant

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('', methods=['POST'])
@jwt_required()
def create_job():
    """Create a new job posting for a recruiter."""
    data = request.get_json() or {}
    user_id = get_jwt_identity()
    print('Create job request - JWT identity:', user_id)
    if str(user_id) != str(data.get('recruiter_id')):
        return jsonify({"error": "Unauthorized: recruiter ID mismatch"}), 403

    recruiter = Recruiter.query.get(user_id)
    if not recruiter:
        return jsonify({"error": "Recruiter not found"}), 404

    salary_min = data.get('salary_min') if data.get('salary_min') not in (None, "", False) else None
    salary_max = data.get('salary_max') if data.get('salary_max') not in (None, "", False) else None

    if salary_min is not None and salary_max is not None:
        try:
            salary_min_value = float(salary_min)
            salary_max_value = float(salary_max)
        except (TypeError, ValueError):
            return jsonify({"error": "Salary values must be numeric"}), 400

        if salary_min_value > salary_max_value:
            return jsonify({"error": "Minimum salary cannot be greater than maximum salary"}), 400

    job = Job(
        recruiter_id=user_id,
        title=data.get('title'),
        description=data.get('description'),
        skills=data.get('skills', []),
        experience_level=data.get('experience_level'),
        job_type=data.get('job_type'),
        location=data.get('location'),
        salary_min=salary_min,
        salary_max=salary_max,
        status='published'
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({
        "job_id": str(job.job_id),
        "status": job.status,
        "message": "Job posted successfully"
    }), 201


@jobs_bp.route('', methods=['GET'])
def list_jobs():
    """Return list of published jobs. Optionally filter by recruiter_id."""
    recruiter_id = request.args.get('recruiter_id')
    query = Job.query.filter_by(status='published')
    if recruiter_id:
        query = query.filter_by(recruiter_id=recruiter_id)
    jobs = query.order_by(Job.created_at.desc()).all()
    job_list = []
    for job in jobs:
        job_list.append({
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
    return jsonify({"jobs": job_list}), 200


@jobs_bp.route('/<job_id>/apply', methods=['POST'])
@jwt_required()
def apply_to_job(job_id):
    """POST /api/jobs/<job_id>/apply
    Applicant applies to a job using their latest uploaded resume (or a custom resume_id).
    """
    applicant_id = get_jwt_identity()

    job = Job.query.get(job_id)
    if not job or job.status != 'published':
        return jsonify({"error": "Job not found or no longer available"}), 404

    # Prevent duplicate applications
    existing = Application.query.filter_by(job_id=job_id, applicant_id=applicant_id).first()
    if existing:
        return jsonify({"error": "You have already applied to this job"}), 409

    # Get resume_id from payload if passed
    import uuid
    data = request.get_json(silent=True) or {}
    resume_id = data.get("resume_id")

    import uuid
    try:
        uuid_job_id = uuid.UUID(job_id)
        uuid_applicant_id = uuid.UUID(applicant_id)
    except ValueError:
        return jsonify({"error": "Invalid job or applicant ID format"}), 400

    if resume_id:
        try:
            uuid_resume_id = uuid.UUID(resume_id)
        except ValueError:
            return jsonify({"error": "Invalid resume ID format"}), 400
        resume = Resume.query.get(uuid_resume_id)
        if not resume or str(resume.applicant_id) != str(uuid_applicant_id):
            return jsonify({"error": "Invalid resume ID"}), 400
    else:
        # Get latest resume for this applicant
        resume = (
            Resume.query
            .filter_by(applicant_id=uuid_applicant_id)
            .order_by(Resume.uploaded_at.desc())
            .first()
        )

    application = Application(
        job_id=uuid_job_id,
        applicant_id=uuid_applicant_id,
        resume_id=resume.resume_id if resume else None,
        status='applied'
    )
    db.session.add(application)
    db.session.commit()

    return jsonify({
        "application_id": str(application.application_id),
        "job_id": str(application.job_id),
        "status": application.status,
        "message": "Application submitted successfully"
    }), 201


@jobs_bp.route('/<job_id>/apply', methods=['DELETE'])
@jwt_required()
def cancel_application(job_id):
    """DELETE /api/jobs/<job_id>/apply
    Applicant cancels their own application for a job.
    """
    applicant_id = get_jwt_identity()

    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    application = Application.query.filter_by(job_id=job_id, applicant_id=applicant_id).first()
    if not application:
        return jsonify({"error": "Application not found"}), 404

    db.session.delete(application)
    db.session.commit()

    return jsonify({
        "message": "Application cancelled successfully",
        "job_id": job_id,
        "application_id": str(application.application_id)
    }), 200


@jobs_bp.route('/<job_id>', methods=['DELETE'])
@jwt_required()
def cancel_job(job_id):
    """DELETE /api/jobs/<job_id>
    Recruiter cancels their own published job.
    """
    recruiter_id = get_jwt_identity()
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if str(job.recruiter_id) != str(recruiter_id):
        return jsonify({"error": "Unauthorized"}), 403
    if job.status != 'published':
        return jsonify({"error": "Job cannot be cancelled"}), 400

    job.status = 'cancelled'
    db.session.commit()

    return jsonify({
        "job_id": str(job.job_id),
        "status": job.status,
        "message": "Job cancelled successfully"
    }), 200


@jobs_bp.route('/<job_id>/score-resume', methods=['POST'])
@jwt_required()
def score_resume_for_job(job_id):
    """POST /api/jobs/<job_id>/score-resume
    Score a resume (existing by resume_id or newly uploaded) against a job's requirements.
    """
    applicant_id = get_jwt_identity()
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    import uuid
    import os
    from app.services.resume_parser import parse_resume

    resume = None
    if 'file' in request.files:
        file = request.files['file']
        if not file.filename:
            return jsonify({"error": "Empty file name"}), 400
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF files are supported"}), 400

        UPLOAD_FOLDER = "uploads"
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        unique_name = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(filepath)

        try:
            parsed_data = parse_resume(filepath)
        except Exception as e:
            return jsonify({"error": f"Failed to parse resume: {str(e)}"}), 500

        if "error" in parsed_data:
            return jsonify(parsed_data), 400

        skills = parsed_data.get("skills", [])
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
    else:
        resume_id = request.form.get("resume_id")
        if not resume_id and request.is_json:
            resume_id = request.json.get("resume_id")

        if resume_id:
            resume = Resume.query.get(resume_id)
            if not resume or str(resume.applicant_id) != str(applicant_id):
                return jsonify({"error": "Invalid resume ID"}), 400
        else:
            resume = (
                Resume.query
                .filter_by(applicant_id=applicant_id)
                .order_by(Resume.uploaded_at.desc())
                .first()
            )

    if not resume:
        return jsonify({"error": "No resume found. Please upload one."}), 400

    job_skills = set(s.lower() for s in (job.skills or []))
    candidate_skills = set(s.lower() for s in (resume.skills or []))
    matched = sorted(list(job_skills & candidate_skills))
    missing = sorted(list(job_skills - candidate_skills))
    match_score = round((len(matched) / len(job_skills) * 100) if job_skills else 0)

    # Let's create or update the Analysis object so the applicant can see it
    # We check if an analysis already exists for this resume and job description (simulate or create)
    from app.models import Analysis
    from app.utils.scorer import score_format, overall_score
    from app.utils.feedback import generate_feedback
    
    # We parse/recreate the analysis object for applicant dashboard metrics
    fmt_score = score_format({"skills": resume.skills or [], "experience": resume.experience_years or 0})
    overall = overall_score(match_score, fmt_score)
    suggestions = generate_feedback(missing, overall)

    analysis = Analysis(
        resume_id=resume.resume_id,
        jd_text=job.description or "",
        match_score=match_score,
        format_score=fmt_score,
        overall_score=overall,
        matched_skills=matched,
        missing_skills=missing,
        suggestions=suggestions
    )
    db.session.add(analysis)
    db.session.commit()

    return jsonify({
        "resume_id": str(resume.resume_id),
        "match_score": match_score,
        "skills": list(candidate_skills),
        "matched_skills": matched,
        "missing_skills": missing,
        "experience_years": float(resume.experience_years) if resume.experience_years else 0,
        "filename": os.path.basename(resume.file_path) if resume.file_path else "Resume"
    }), 200



@jobs_bp.route('/<job_id>/applications', methods=['GET'])
@jwt_required()
def get_job_applications(job_id):
    """GET /api/jobs/<job_id>/applications
    Returns all applicants for a recruiter's job, ranked by skill match score.
    """
    recruiter_id = get_jwt_identity()

    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if str(job.recruiter_id) != str(recruiter_id):
        return jsonify({"error": "Unauthorized"}), 403

    applications = Application.query.filter_by(job_id=job_id).order_by(Application.applied_at.desc()).all()

    job_skills = set(s.lower() for s in (job.skills or []))

    from app.utils.scorer import score_experience, composite_ranking_score, cosine_similarity

    results = []
    for app in applications:
        applicant = Applicant.query.get(app.applicant_id)
        resume = Resume.query.get(app.resume_id) if app.resume_id else None

        # If applicant has no dedicated resume linked, grab their latest
        if not resume:
            resume = (
                Resume.query
                .filter_by(applicant_id=app.applicant_id)
                .order_by(Resume.uploaded_at.desc())
                .first()
            )

        candidate_skills = set(s.lower() for s in (resume.skills or [] if resume else []))

        matched = sorted(list(job_skills & candidate_skills))
        missing = sorted(list(job_skills - candidate_skills))
        match_score = round((len(matched) / len(job_skills) * 100) if job_skills else 0)

        experience_yrs = float(resume.experience_years) if resume and resume.experience_years else 0
        exp_score = score_experience(experience_yrs, job.experience_level)
        cosine_score = cosine_similarity(list(candidate_skills), list(job_skills))
        comp_score = composite_ranking_score(match_score, exp_score, cosine_score)

        results.append({
            "application_id": str(app.application_id),
            "applicant_id": str(app.applicant_id),
            "name": (applicant.name or resume.name or "Unknown") if applicant else (resume.name if resume else "Unknown"),
            "email": (applicant.email or resume.email or "") if applicant else (resume.email if resume else ""),
            "phone": (applicant.phone or resume.phone or "") if applicant else (resume.phone if resume else ""),
            "skills": list(candidate_skills),
            "matched_skills": matched,
            "missing_skills": missing,
            "match_score": match_score,
            "cosine_similarity": cosine_score,
            "experience_years": experience_yrs,
            "experience_score": exp_score,
            "composite_score": comp_score,
            "status": app.status,
            "applied_at": app.applied_at.isoformat() if app.applied_at else "",
        })

    # Sort by composite score (skill match 70% + experience fit 30%) descending
    results.sort(key=lambda x: x["composite_score"], reverse=True)

    return jsonify({
        "job_id": job_id,
        "job_title": job.title,
        "job_skills": list(job.skills or []),
        "applications": results,
        "total": len(results)
    }), 200


@jobs_bp.route('/<job_id>/applications/<application_id>', methods=['PATCH'])
@jwt_required()
def update_application_status(job_id, application_id):
    """PATCH /api/jobs/<job_id>/applications/<application_id>
    Recruiter updates candidate status: shortlisted | rejected | reviewed | applied
    """
    recruiter_id = get_jwt_identity()

    job = Job.query.get(job_id)
    if not job or str(job.recruiter_id) != str(recruiter_id):
        return jsonify({"error": "Unauthorized"}), 403

    application = Application.query.get(application_id)
    if not application or str(application.job_id) != str(job_id):
        return jsonify({"error": "Application not found"}), 404

    data = request.get_json() or {}
    new_status = data.get('status')
    if new_status not in ('applied', 'reviewed', 'shortlisted', 'rejected'):
        return jsonify({"error": "Invalid status"}), 400

    application.status = new_status
    db.session.commit()

    return jsonify({"application_id": str(application.application_id), "status": application.status}), 200


