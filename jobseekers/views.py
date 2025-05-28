from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from jobseekers.models import Jobseeker, AdditionalInfo
from jobs.utils import calculate_match_score
from datetime import datetime
from jobs.models import *
from resumes.models import *

@login_required
def profile_builder(request):
    user = request.user

    try:
        jobseeker = user.jobseeker
    except Jobseeker.DoesNotExist:
        jobseeker = None  # আমরা POST-এর সময় তৈরি করব

    if request.method == 'POST':
        if not jobseeker:
            jobseeker = Jobseeker(user=user)

        # প্রোফাইল তথ্য সংরক্ষণ
        jobseeker.full_name = request.POST.get('full_name')
        jobseeker.date_of_birth = request.POST.get('dob')
        jobseeker.gender = request.POST.get('gender')
        jobseeker.contact_number = request.POST.get('contact')
        jobseeker.address = request.POST.get('address')
        jobseeker.job_type_preference = request.POST.get('job_type')
        jobseeker.preferred_country = request.POST.get('preferred_country')
        jobseeker.preferred_city = request.POST.get('preferred_city')
        jobseeker.passport_number = request.POST.get('passport')
        jobseeker.national_id = request.POST.get('nid')

        if request.FILES.get('document'):
            jobseeker.document_upload = request.FILES['document']

        # তারিখ সঠিক ফর্ম্যাটে রূপান্তর
        if isinstance(jobseeker.date_of_birth, str):
            try:
                jobseeker.date_of_birth = datetime.strptime(jobseeker.date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                pass  # ভুল ডেট থাকলে save এর আগে error handle করুন

        jobseeker.save()

        # অতিরিক্ত তথ্য
        about = request.POST.get('about_me')
        achievements = request.POST.get('achievements')
        hobbies = request.POST.get('hobbies')

        AdditionalInfo.objects.update_or_create(
            jobseeker=jobseeker,
            defaults={
                'about_me': about,
                'achievements': achievements,
                'hobbies': hobbies
            }
        )

        return redirect('jobseeker:profile_view')

    return render(request, 'jobseekers/profile_builder.html', {'jobseeker': jobseeker})

@login_required
def profile_view(request):
    try:
        jobseeker = request.user.jobseeker
    except:
        jobseeker = None

    additional_info = None
    if jobseeker:
        additional_info = getattr(jobseeker, 'additionalinfo', None)

    return render(request, 'jobseekers/profile_view.html', {
        'jobseeker': jobseeker,
        'additional_info': additional_info
    })

@login_required
def dashboard(request):
    try:
        jobseeker = request.user.jobseeker
    except Jobseeker.DoesNotExist:
        messages.warning(request, "Please complete your profile first.")
        return redirect('jobseeker:profile_builder')

    resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()
    resume_skills = resume.skills if resume else ''
    resume_exp = resume.experience if resume else ''
    country = jobseeker.preferred_country or ''
    city = jobseeker.preferred_city or ''

    jobs = Job.objects.filter(status='active').order_by('-posted_at')

    recommended = []
    for job in jobs:
        score = calculate_match_score(job.skills, resume_skills, resume_exp)
        if country.lower() in (job.country or '').lower():
            score += 0.1
        if city.lower() in (job.city or '').lower():
            score += 0.1
        if score >= 0.3:
            job.match_score = round(score * 100)
            recommended.append(job)

    recommended = sorted(recommended, key=lambda j: j.match_score, reverse=True)

    return render(request, 'jobseekers/dashboard.html', {
        'jobseeker': jobseeker,
        'recommended_jobs': recommended[:6]  # Show top 6
    })