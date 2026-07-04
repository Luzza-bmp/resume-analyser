def generate_feedback(missing_skills: list, overall_score: float) -> list:
    tips = []

    for skill in missing_skills:
        tips.append(f"Consider adding {skill} to your resume if you have relevant experience.")

    if overall_score < 50:
        tips.append("Your overall match is low — try tailoring this resume specifically for this job description.")

    if not tips:
        tips.append("Good match! Consider quantifying your achievements with numbers.")

    return tips