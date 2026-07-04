from app import db
from app.models import Resume, Analysis


def save_resume(applicant_id, filepath, raw_text, parsed_data):
    resume = Resume(
        applicant_id=applicant_id,
        file_path=filepath,
        raw_text=raw_text,
        name=parsed_data.get("name"),
        email=parsed_data.get("email"),
        phone=parsed_data.get("phone"),
        experience_years=parsed_data.get("experience"),
        skills=parsed_data.get("skills", [])
    )
    db.session.add(resume)
    db.session.commit()
    return resume


def save_analysis(resume_id, jd_text, match_score, format_score, overall_score,
                   matched_skills, missing_skills, suggestions):
    analysis = Analysis(
        resume_id=resume_id,
        jd_text=jd_text,
        match_score=match_score,
        format_score=format_score,
        overall_score=overall_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        suggestions=suggestions
    )
    db.session.add(analysis)
    db.session.commit()
    return analysis