def calculate_match_score(resume_skills: list, jd_skills: list) -> float:
    """% of JD skills that also appear in the resume."""
    if not jd_skills:
        return 0.0
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)
    matched = resume_set & jd_set
    return round(len(matched) / len(jd_set) * 100, 2)


def get_missing_skills(resume_skills: list, jd_skills: list) -> list:
    return sorted(list(set(jd_skills) - set(resume_skills)))


def get_matched_skills(resume_skills: list, jd_skills: list) -> list:
    return sorted(list(set(resume_skills) & set(jd_skills)))


def score_format(parsed_data: dict) -> float:
    """Basic completeness check — 20 points per section present."""
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


def overall_score(match_score: float, format_score: float) -> float:
    """Weighted composite: 70% keyword match, 30% format."""
    return round(match_score * 0.70 + format_score * 0.30, 2)