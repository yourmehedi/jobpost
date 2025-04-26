def get_employer_limits(employer):
    limits = {
        'direct': {'job_limit': 5, 'resume_limit': 10},
        'agency_local': {'job_limit': 15, 'resume_limit': 30},
        'agency_overseas': {'job_limit': 30, 'resume_limit': 100},
    }
    return limits.get(employer.employer_type, {'job_limit': 0, 'resume_limit': 0})
