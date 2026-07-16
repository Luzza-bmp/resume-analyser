from app.utils.scorer import cosine_similarity, composite_ranking_score


def test_cosine_similarity_uses_shared_skills():
    score = cosine_similarity(["python", "sql", "react"], ["python", "react", "docker"])
    assert score == 66.67


def test_composite_ranking_includes_cosine_similarity():
    score = composite_ranking_score(80, 70, 60)
    assert score == 72.0
