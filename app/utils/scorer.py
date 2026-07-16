import math


def calculate_match_score(resume_skills, jd_skills):
    if not jd_skills:
        return 0.0
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)
    matched = resume_set & jd_set
    return round(len(matched) / len(jd_set) * 100, 2)


def cosine_similarity(resume_skills, jd_skills):
    """Return cosine similarity between two skill lists as a percentage."""
    if not jd_skills:
        return 0.0

    resume_vector = {skill.lower().strip(): 1 for skill in resume_skills if skill}
    jd_vector = {skill.lower().strip(): 1 for skill in jd_skills if skill}

    if not resume_vector or not jd_vector:
        return 0.0

    shared = set(resume_vector) & set(jd_vector)
    if not shared:
        return 0.0

    dot_product = len(shared)
    magnitude = math.sqrt(len(resume_vector) * len(jd_vector))
    return round((dot_product / magnitude) * 100, 2)


def get_missing_skills(resume_skills, jd_skills):
    return sorted(list(set(jd_skills) - set(resume_skills)))


def get_matched_skills(resume_skills, jd_skills):
    return sorted(list(set(resume_skills) & set(jd_skills)))


# Maps experience_level field values to (min_years, max_years) ranges
EXPERIENCE_LEVEL_MAP = {
    "fresher": (0, 1),
    "1-3":     (1, 3),
    "3-5":     (3, 5),
    "5+":      (5, 99),
}


def score_experience(candidate_years: float, job_experience_level: str) -> float:
    """
    Returns an experience score 0-100 based on how well the candidate's
    extracted years match the job's required experience level.

    Scoring logic:
    - Candidate meets the range fully         → 100
    - Candidate is within 1 year below min    → 70  (almost there)
    - Candidate is within 2 years below min   → 40  (under-qualified)
    - Candidate is 2+ years below min         → 10  (significantly under-qualified)
    - Candidate is over the max (over-qualified) → 80 (slight penalty, still capable)
    - No experience_level set on job          → 100 (no requirement = full marks)
    """
    if not job_experience_level:
        return 100.0

    level = job_experience_level.lower().strip()
    if level not in EXPERIENCE_LEVEL_MAP:
        return 100.0  # Unknown level → no penalty

    min_years, max_years = EXPERIENCE_LEVEL_MAP[level]
    years = float(candidate_years or 0)

    if min_years <= years <= max_years:
        return 100.0
    elif years > max_years:
        # Over-qualified — still capable, small penalty
        return 80.0
    else:
        gap = min_years - years
        if gap <= 1:
            return 70.0
        elif gap <= 2:
            return 40.0
        else:
            return 10.0


def score_format(parsed_data):
    score = 0
    if parsed_data.get("name"):
        score += 20
    if parsed_data.get("email"):
        score += 20
    if parsed_data.get("education"):
        score += 20
    if parsed_data.get("experience") is not None:
        score += 20
    if parsed_data.get("skills"):
        score += 20
    return min(score, 100)


def overall_score(match_score, format_score):
    return round(match_score * 0.70 + format_score * 0.30, 2)


def composite_ranking_score(match_score: float, experience_score: float, cosine_score: float = 0.0) -> float:
    """
    Composite score used ONLY for ranking candidates in the recruiter view.
    Weights:
      - Skill match score : 60%
      - Cosine similarity : 20%
      - Experience score  : 20%
    """
    return round(match_score * 0.60 + cosine_score * 0.20 + experience_score * 0.20, 2)
