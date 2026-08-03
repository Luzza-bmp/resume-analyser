# SipSetu — Architecture, Scoring & Ranking (Detailed)

This document explains how the SipSetu resume parsing, skill extraction, scoring and candidate ranking work today in this repository. It references key implementation files and gives math, examples, and suggestions for improvement.

---

**Primary files to inspect**

- Backend scoring and helpers: [app/utils/scorer.py](app/utils/scorer.py#L1-L200)
- Skill extraction / lookup: [app/services/skill_matcher.py](app/services/skill_matcher.py#L1-L800)
- Job routes and scoring usage: [app/routes/jobs.py](app/routes/jobs.py#L1-L260)
- Resume parsing entrypoint: [app/services/resume_parser.py](app/services/resume_parser.py#L1-L200)

---

## High-level pipeline

1. Resume ingestion: resumes are uploaded (PDF or other) and parsed by the resume parsing service. See [app/services/resume_parser.py](app/services/resume_parser.py#L1-L200).
2. Skill extraction: parsed text is normalized to lower-case and searched against a curated skill set (`SKILLS_DB`) using word-boundary regex matches. See [app/services/skill_matcher.py](app/services/skill_matcher.py#L1-L800).
3. Feature extraction: structured fields are pulled from the parsed data (name, email, education, experience years, skills array).
4. Scoring: multiple small scorers compute skill match percentage, cosine similarity, experience score, format score, and composite ranking. Implementations are in [app/utils/scorer.py](app/utils/scorer.py#L1-L200).
5. Ranking: recruiter-facing ranking uses a composite score (weighted combination) to order candidates.

---

## Skill extraction (exact mechanism)

- `SKILLS_DB` is a large set of canonical skill strings (programming languages, frameworks, cloud, soft skills, languages, etc.) defined in [app/services/skill_matcher.py](app/services/skill_matcher.py#L1-L800).
- Extraction algorithm (function `extract_skills(text)`):
  - Convert `text` to lower-case.
  - For each `skill` in `SKILLS_DB` run a regex search using a word-boundary pattern: `\b{re.escape(skill)}\b`.
  - If the regex matches, add that `skill` to the set of found skills.
  - Return a sorted, deduplicated list of found skills.

Notes and limitations:
- This is exact-token matching. Multi-word skills (e.g. "machine learning") are matched as exact phrases if present.
- It does not perform fuzzy matching, stemming, synonym normalization, or semantic mapping (e.g. "tf" → "tensorflow").

---

## Scoring functions (source + detailed explanation)

All scoring functions are in [app/utils/scorer.py](app/utils/scorer.py#L1-L200). Below we reproduce the logic and explain the math.

### 1) Match score — `calculate_match_score(resume_skills, jd_skills)`

Code summary:
- If `jd_skills` is empty → returns `0.0`.
- Compute sets `resume_set` and `jd_set`.
- `matched = resume_set & jd_set` (intersection).
- Return `len(matched) / len(jd_set) * 100`, rounded to 2 decimals.

Interpretation:
- This is a simple precision-like metric: percentage of job-required skills present in the resume.
- Example: JD requires `['python','sql','aws']` and resume has `['python','excel']` → matched = `{'python'}` → score = 1/3 * 100 = 33.33%

Pros / Cons:
- Pros: easy to interpret, emphasizes covering required skills.
- Cons: treats all skills equally, doesn't reward resumes that have many related skills beyond the JD, and is susceptible to false negatives when synonyms are used.

### 2) Cosine similarity — `cosine_similarity(resume_skills, jd_skills)` (TF–IDF)

Code summary:
- If `jd_skills` empty → `0.0`.
- The repository now computes a TF–IDF weighted cosine similarity over the two-document corpus (the resume and the JD). For each term (skill) the pipeline:
   - normalizes terms to lower-case,
   - computes term frequency (TF) per document,
   - computes document frequency (DF) across the two documents,
   - computes a smoothed IDF: `idf = log((1 + N) / (1 + df)) + 1` with `N=2`,
   - forms TF–IDF vectors and computes cosine similarity between them,
   - returns cosine * 100 rounded to 2 decimals.

Implementation: see the TF–IDF cosine code in [app/utils/scorer.py](app/utils/scorer.py#L1-L200).

Mathematical derivation:
- Let a and b be TF–IDF vectors derived from the resume and JD vocabularies. Cosine similarity is still:
   $$\\mathrm{cosine}(a,b) = \\frac{a\\cdot b}{\\|a\\|\\,\\|b\\|}$$

Example (intuition):
- Terms that appear in both documents get positive TF–IDF contributions to the dot product.
- Terms that are common to both documents (df=2) receive a smaller IDF, so rare discriminative skills increase similarity more than ubiquitous ones.

Interpretation:
- TF–IDF makes cosine similarity more informative than the previous binary overlap: it downweights very common terms and upweights rarer, discriminative skills. This helps differentiate candidates who share common skills but vary on niche qualifications.

### 3) Missing / Matched skills helpers

- `get_missing_skills(resume_skills, jd_skills)` returns sorted list of skills in JD but not in resume: `JD \ Resume`.
- `get_matched_skills` returns intersection sorted: `Resume ∩ JD`.

These are used to show feedback and suggestions on the UI.

### 4) Experience scoring — `score_experience(candidate_years, job_experience_level)`

Mapping:
- The code maps textual `experience_level` to numeric ranges via `EXPERIENCE_LEVEL_MAP`:
  - `fresher`: (0,1)
  - `1-3`: (1,3)
  - `3-5`: (3,5)
  - `5+`: (5,99)

Logic:
- If job has no level → returns 100 (no penalty).
- If candidate years lie within range → 100.
- If candidate years > max → 80 (slight penalty for being over-qualified).
- If candidate is below min:
  - within 1 year → 70
  - within 2 years → 40
  - more than 2 years below → 10

Interpretation:
- Conservative scoring that favors meeting the exact requirement and penalizes under-experience harshly while mildly penalizing over-experience.

### 5) Format score — `score_format(parsed_data)`

- Gives up to 100 points, with 5 buckets of 20 each for presence of: `name`, `email`, `education`, `experience`, and `skills`.
- Example: a parsed resume with name, email and skills but missing education and experience → 60/100.

Purpose:
- Measures completeness / parse quality; used to encourage good formatted resumes and penalize poorly parsed or incomplete submissions.

### 6) Overall and composite scores

- `overall_score(match_score, format_score)`:
  - Weighted sum: `match_score * 0.70 + format_score * 0.30` (rounded to 2 decimals).
  - Purpose: combine skill coverage with resume quality.

- `composite_ranking_score(match_score, experience_score, cosine_score=0.0)`:
  - Weights: skill match 60%, cosine 20%, experience 20%.
  - Formula: `match_score * 0.60 + cosine_score * 0.20 + experience_score * 0.20`.
  - Used to rank candidates for recruiter views (gives more weight to raw matching, but includes similarity and experience).

Rationale:
- `match_score` is prioritized because meeting explicit JD skills is business-critical.
- `cosine_score` accounts for the overlap normalized by profile breadth (penalizes noisy resumes with many unrelated skills).
- `experience_score` ensures years-of-experience compatibility is considered.

---

## End-to-end ranking example

Given:
- JD skills: `['python', 'sql', 'aws']` (|JD|=3)
- Candidate A skills: `['python', 'sql']`
  - match_score = 2/3 * 100 = 66.67
  - cosine = 2 / sqrt(2*3) = 2 / sqrt(6) ≈ 0.8165 → 81.65%
  - experience_score (assume 2 years vs JD `1-3`) = 100
  - composite = 66.67*0.6 + 81.65*0.2 + 100*0.2 = 40.00 + 16.33 + 20 = 76.33

- Candidate B skills: `['python', 'aws', 'docker', 'kubernetes']`
  - match_score = 2/3 * 100 = 66.67 (matches python and aws)
  - cosine = 2 / sqrt(4*3) = 2 / sqrt(12) ≈ 57.74%
  - experience_score = 80 (if over-qualified)
  - composite = 66.67*0.6 + 57.74*0.2 + 80*0.2 = 40.00 + 11.55 + 16.00 = 67.55

Ranking: Candidate A > Candidate B because A's cosine similarity is higher and experience_score met the range.

---

## How the code is used in routes

- When scoring a resume for a job, the route `POST /api/jobs/<job_id>/score-resume` in [app/routes/jobs.py](app/routes/jobs.py#L1-L260) will parse or accept a resume, extract skills and fields, then compute these metrics. The route saves `Resume` rows and may return the computed scores.
- Recruiter dashboard (`app/routes/recruiter_dashboard.py`) fetches candidate data and uses `composite_ranking_score` to sort `top_candidates` before delivering them to the frontend. The frontend then renders the list ordered by composite ranking.

---

## Practical implications and known issues

1. Exact matching vs synonyms:
   - Current approach requires exact phrase matches from `SKILLS_DB`. "PyTorch" vs "pytorch" works since case-insensitive, but synonyms or abbreviations (e.g., "tf" for "tensorflow") will be missed.
2. Multi-word skill detection:
   - `re.search(r"\b{skill}\b")` handles multi-word phrases but can have false negatives with punctuation or line-break tokenization.
3. No IDF or rare-skill weighting:
   - All skills are weighted equally. A match on a rare, high-value skill (e.g., "kubernetes") is treated the same as a common one (e.g., "ms office").
4. Binary vectors for cosine:
   - The cosine implementation uses binary presence indicators only. It does not account for frequency or importance of a skill within the doc.
5. Experience ranges are coarse:
   - The `EXPERIENCE_LEVEL_MAP` is a small set; many job postings use custom ranges or decimals (1.5 years), so mapping may be imprecise.
6. Format score is heuristic and coarse-grained.

---

## Suggested improvements (short and actionable)

1. Add fuzzy matching / token normalization:
   - Use `rapidfuzz` or `fuzzywuzzy` to map near-matches (e.g., "kube" → "kubernetes").
   - Normalize hyphens, slashes, and punctuation before matching.

2. Add synonym and alias dictionary:
   - Map aliases ("tf" → "tensorflow", "aws" ↔ "amazon web services", "react" ↔ "reactjs").

3. Use TF–IDF / weighted vectors for cosine:
   - Build a vocabulary across JDs and resumes and compute TF–IDF vectors so rare, discriminative skills get higher weight.
   - This will change cosine to a more informative score than binary overlap.

4. Add skill importance weighting from JD:
   - Allow job posters to mark skills as `required`, `preferred`, or `bonus` and weight match_score accordingly (required skills multiply the match contribution).

5. Improve experience handling:
   - Parse and store exact years (floats), allow custom ranges, and compute a smooth penalty using a decaying function rather than step buckets.

6. Add named entity / phrase extraction improvements:
   - Use spaCy + custom matcher or transformer-backed NER to extract skills more robustly from noisy text.

7. Cache expensive operations:
   - Cache parsed resume skills and computed vectors to avoid recomputing on repeated scoring.

8. Provide explainability data to recruiters:
   - Return breakdowns (matched skill list, missing skills, experience delta, format sections) with scores to enable fast decisions.

---

## Where to change weights and behavior

- Change composite ranking weights in [app/utils/scorer.py](app/utils/scorer.py#L1-L200) inside `composite_ranking_score`.
- Change match vs format weighting in `overall_score`.
- Add new features (TF-IDF, fuzzy matching) by modifying `app/services/skill_matcher.py` and adding a new vectorizer utility module.

---

## Quick references (code snippets)

- Cosine implementation (binary vectors):

$$\text{cosine\\_similarity} = \frac{|A\cap B|}{\sqrt{|A|\cdot|B|}} \times 100$$

- Match percentage:

$$\text{match\\_score} = \frac{|A\cap B|}{|B|} \times 100$$

- Composite ranking:

$$\text{composite} = 0.60\times\text{match} + 0.20\times\text{cosine} + 0.20\times\text{experience}$$

- Overall (match + format):

$$\text{overall} = 0.70\times\text{match} + 0.30\times\text{format}$$

---

If you want, I can:

- implement TF–IDF vectorization and swap in TF–IDF cosine scoring,
- add fuzzy-synonym mapping and show before/after ranking diffs,
- produce a per-field explainability JSON returned by `POST /api/jobs/<job_id>/score-resume`.

Tell me which improvement you'd like me to implement next and I'll add a plan and patch the code. 
