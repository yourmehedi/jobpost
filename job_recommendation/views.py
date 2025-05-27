from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from jobseekers.models import Jobseeker
from jobs.models import Job
from resumes.models import Resume
from jobs.utils import calculate_match_score
from subscriptions.models import Subscription
from django.contrib import messages

def has_valid_ai_token(user):
    sub = Subscription.objects.filter(employer=user, active=True).first()
    return sub and sub.ai_tokens > 0

@login_required
def recommended_jobs(request):
    try:
        jobseeker = request.user.jobseeker
    except Jobseeker.DoesNotExist:
        messages.error(request, "Please complete your jobseeker profile first.")
        return render(request, 'job_recommendation/no_profile.html')

    # Resume বা Preferred Info
    resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()
    resume_skills = resume.skills if resume else ''
    resume_exp = resume.experience if resume else ''
    job_type = jobseeker.job_type_preference
    country = jobseeker.preferred_country or ''
    city = jobseeker.preferred_city or ''

    # সব জব আনো
    jobs = Job.objects.filter(status='active').order_by('-posted_at')

    recommended = []
    for job in jobs:
        score = calculate_match_score(job.skills, resume_skills, resume_exp)
        location_match = 0
        if country.lower() in (job.country or '').lower():
            location_match += 0.1
        if city.lower() in (job.city or '').lower():
            location_match += 0.1

        score += location_match

        if score >= 0.3:  # থ্রেশহোল্ড
            job.match_score = round(score * 100)
            recommended.append(job)

    recommended = sorted(recommended, key=lambda j: j.match_score, reverse=True)
    
    return render(request, 'job_recommendation/recommendations.html', {
        'recommended_jobs': recommended,
        'jobseeker': jobseeker
    })
