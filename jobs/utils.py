import re
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Employer posting limits
def get_employer_limits(employer):
    limits = {
        'direct': {'job_limit': 5, 'resume_limit': 10},
        'agency_local': {'job_limit': 15, 'resume_limit': 30},
        'agency_overseas': {'job_limit': 30, 'resume_limit': 100},
        'government': {'job_limit': 50, 'resume_limit': 200},
    }
    return limits.get(employer.employer_type, {'job_limit': 0, 'resume_limit': 0})


# Load once globally for better performance
try:
    embedding_model = pipeline("feature-extraction", model="sentence-transformers/all-MiniLM-L6-v2")
except Exception as e:
    print("⚠️ Hugging Face model load failed:", e)
    embedding_model = None


def text_to_vector(text: str):
    """Convert text to embedding vector using Hugging Face"""
    if not text or not embedding_model:
        return np.zeros((1, 384))
    vec = embedding_model(text[:512])[0]  # limit length
    return np.mean(vec, axis=0).reshape(1, -1)


def calculate_match_score(job_skills: str, resume_skills: str, resume_experience: str) -> int:
    """
    Hybrid matching:
      1️⃣  Keyword overlap
      2️⃣  Semantic similarity (AI)
      3️⃣  Experience bonus
    """
    if not job_skills or not resume_skills:
        return 0

    # Keyword overlap 
    job_keywords = [s.strip().lower() for s in job_skills.split(',')]
    user_skills = [s.strip().lower() for s in resume_skills.split(',')]
    matched = set(job_keywords) & set(user_skills)
    keyword_score = (len(matched) / len(job_keywords)) * 100 if job_keywords else 0

    # Semantic similarity (AI match) 
    job_vec = text_to_vector(", ".join(job_keywords))
    resume_vec = text_to_vector(resume_skills)
    semantic_score = float(cosine_similarity(job_vec, resume_vec)[0][0]) * 100

    # Bonus for experience
    exp_bonus = 10 if resume_experience and len(resume_experience) > 50 else 0

    # Final weighted score
    final_score = (keyword_score * 0.5) + (semantic_score * 0.4) + exp_bonus
    return int(min(100, round(final_score)))
