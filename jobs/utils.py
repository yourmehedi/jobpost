def get_employer_limits(employer):
    limits = {
        'direct': {'job_limit': 5, 'resume_limit': 10},
        'agency_local': {'job_limit': 15, 'resume_limit': 30},
        'agency_overseas': {'job_limit': 30, 'resume_limit': 100},
    }
    return limits.get(employer.employer_type, {'job_limit': 0, 'resume_limit': 0})

def calculate_match_score(job_skills: str, resume_skills: str, resume_experience: str) -> int:
    if not job_skills or not resume_skills:
        return 0

    job_keywords = [s.strip().lower() for s in job_skills.split(',')]
    user_skills = [s.strip().lower() for s in resume_skills.split(',')]

    matched = set(job_keywords) & set(user_skills)
    skill_score = (len(matched) / len(job_keywords)) * 100 if job_keywords else 0

    # Optional: Give bonus for having experience
    exp_bonus = 10 if resume_experience and len(resume_experience) > 50 else 0

    return min(100, round(skill_score + exp_bonus))
