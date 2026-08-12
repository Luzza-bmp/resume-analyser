import math
from collections import Counter


def calculate_match_score(resume_skills, jd_skills):
    if not jd_skills:
        return 0.0
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)
    matched = resume_set & jd_set
    return round(len(matched) / len(jd_set) * 100, 2)


def cosine_similarity(resume_skills, jd_skills):
    """Compute cosine similarity between a resume and JD using a simple TF–IDF weighting.

    This replaces the previous binary-presence cosine with TF–IDF computed over the
    two-document corpus (resume, jd). Returns a percentage (0-100).
    """
    if not jd_skills:
        return 0.0

    # normalize terms
    resume_terms = [s.lower().strip() for s in (resume_skills or []) if s]
    jd_terms = [s.lower().strip() for s in (jd_skills or []) if s]

    if not resume_terms or not jd_terms:
        return 0.0

    # Vocabulary is the union of terms
    vocab = list(sorted(set(resume_terms) | set(jd_terms)))

    # Term frequencies (TF)
    tf_resume = Counter(resume_terms)
    tf_jd = Counter(jd_terms)

    # Document frequencies (DF) over the two-doc corpus
    df = {}
    for term in vocab:
        df_count = 0
        if tf_resume.get(term, 0) > 0:
            df_count += 1
        if tf_jd.get(term, 0) > 0:
            df_count += 1
        df[term] = df_count

    # Smooth IDF: idf = log((1 + N) / (1 + df)) + 1
    N = 2
    idf = {t: math.log((1.0 + N) / (1.0 + df[t])) + 1.0 for t in vocab}

    # Build TF-IDF vectors
    vec_resume = [tf_resume.get(t, 0) * idf[t] for t in vocab]
    vec_jd = [tf_jd.get(t, 0) * idf[t] for t in vocab]

    # Compute dot product and norms
    dot = sum(a * b for a, b in zip(vec_resume, vec_jd))
    norm_r = math.sqrt(sum(a * a for a in vec_resume))
    norm_j = math.sqrt(sum(b * b for b in vec_jd))

    if norm_r == 0 or norm_j == 0:
        return 0.0

    cosine = dot / (norm_r * norm_j)
    return round(cosine * 100, 2)


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
