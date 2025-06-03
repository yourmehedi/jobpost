from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import random
from .models import *
from django.contrib import messages
from .utils import get_employer_limits
from accounts.models import Employer
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from .models import JobApplication
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from resumes.models import Resume  
from moderation.utils import moderate_text
from jobs.utils import calculate_match_score
from subscriptions.models import Subscription
from django.template.loader import render_to_string
from django.http import HttpResponse

def has_valid_ai_token(user):
    sub = Subscription.objects.filter(employer=user, active=True).first()
    return sub and sub.ai_tokens > 0

@login_required
def post_job(request):
    message = None
    companies = Company.objects.all()

    if request.method == 'POST':
        try:
            employer = request.user.management_employer
        except AttributeError:
            message = "You must have an employer account to post a job."
            return render(request, 'jobs/post_job.html', {'companies': companies, 'message': message})

        # Field extraction
        title = request.POST.get('jobTitle')
        company_name = request.POST.get('companyName')
        description = request.POST.get('jobDescription')
        location = request.POST.get('l')
        formatted_address = request.POST.get('formattedAddress')
        salary = request.POST.get('salary')
        is_email_protected = request.POST.get('anonymizeEmail') == 'on'
        skills = request.POST.get('skills')
        tech_stack = ', '.join(request.POST.getlist('stack'))

        try:
            vacancies = int(request.POST.get('vacancies'))
        except (TypeError, ValueError):
            vacancies = 1

        expiry_date_str = request.POST.get('expiry')
        try:
            expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date() if expiry_date_str else None
        except ValueError:
            expiry_date = None

        valid_passport = request.POST.get('valid_passport') == 'on'
        principal = request.POST.get('principal')
        job_role = request.POST.get('job_role')
        experience_level = request.POST.get('experience')
        job_type = request.POST.get('job_type')
        industry = request.POST.get('industry')
        street = request.POST.get('street')
        city = request.POST.get('city')
        province = request.POST.get('province')
        zip_code = request.POST.get('zip')
        country = request.POST.get('country')
        english_required = request.POST.get('english_required') == 'on'

        # ✅ Validation
        required_fields = [title, company_name, description, location]
        if not all(required_fields):
            message = "Please fill in all required fields."
            return render(request, 'jobs/post_job.html', {'companies': companies, 'message': message})

        # ✅ Clean/filter text fields
        # add ai_access
        clean_description = moderate_text(description)
        clean_skills = moderate_text(skills)
        clean_principal = moderate_text(principal)
        clean_title = moderate_text(title)
        clean_company_name = moderate_text(company_name)

        # ✅ Save Job
        company, _ = Company.objects.get_or_create(name=clean_company_name)

        Job.objects.create(
            title=clean_title,
            company=company,
            employer=employer,
            description=clean_description,
            location=location,
            formatted_address=formatted_address,
            salary=salary,
            is_email_protected=is_email_protected,
            skills=clean_skills,
            tech_stack=tech_stack,
            vacancies=vacancies,
            expiry_date=expiry_date,
            valid_passport=valid_passport,
            principal=clean_principal,
            job_role=job_role,
            experience_level=experience_level,
            job_type=job_type,
            industry=industry,
            street=street,
            city=city,
            province=province,
            zip_code=zip_code,
            country=country,
            english_required=english_required,
            posted_by=request.user
        )

        return redirect('jobs:job_post_success')

    return render(request, 'jobs/post_job.html', {'companies': companies, 'message': message})

def job_post_success(request):
    return render(request, 'jobs/job_success.html')

def job_list(request):
    query = request.GET.get('q', '')
    job_queryset = Job.objects.select_related('company').filter(status='active').order_by('-posted_at')

    subscription = Subscription.objects.filter(employer=request.user, active=True).first()

    if query:
        job_queryset = job_queryset.filter(
            Q(title__icontains=query) |
            Q(company__name__icontains=query)
        )

    user_resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()
    resume_skills = user_resume.skills if user_resume else ''
    resume_experience = user_resume.experience if user_resume else ''

    # Get all job IDs saved by current user
    # saved_jobs_ids = set(SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True))

    for job in job_queryset:
        job.skill_list = job.skills.split(",") if job.skills else []
        job.perk_list = job.perks.split(",") if job.perks else []

        if resume_skills:
            job.match_score = calculate_match_score(job.skills, resume_skills, resume_experience)
        else:
            job.match_score = None

        # Mark if this job is saved by the current user
        # job.is_saved = job.id in saved_jobs_ids

    paginator = Paginator(job_queryset, 8)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'query': query,
        'user_subscription': subscription
    })

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job.skill_list = job.skills.split(",") if job.skills else []
    job.perk_list = job.perks.split(",") if job.perks else []
    return render(request, 'jobs/job_detail.html', {'job': job})

def job_detail_modal(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job.skill_list = job.skills.split(",") if job.skills else []
    job.perk_list = job.perks.split(",") if job.perks else []
    return render(request, 'jobs/job_detail_modal.html', {'job': job})

def ajax_job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job.skill_list = job.skills.split(",") if job.skills else []
    job.perk_list = job.perks.split(",") if job.perks else []

    html = render_to_string('jobs/job_detail_modal.html', {'job': job}, request=request)
    return HttpResponse(html)

def apply(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        JobApplication.objects.create(
            job=job,
            name=name,
            email=email,
            message=message
        )

        return render(request, 'jobs/apply_success.html', {'job': job})

    return render(request, 'jobs/apply.html', {'job': job})

@staff_member_required
@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def job_applications_list(request):
    applications = JobApplication.objects.all().order_by('-applied_at')
    return render(request, 'jobs/applications_dashboard.html', {'applications': applications})

@staff_member_required
@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def reply_application(request, application_id):
    app = get_object_or_404(JobApplication, id=application_id)

    if request.method == 'POST':
        app.reply = request.POST.get('reply')
        app.save()
        return redirect('jobs:applications_dashboard')

    return render(request, 'jobs/reply_application.html', {'application': app})

@staff_member_required
@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def delete_application(request, application_id):
    app = get_object_or_404(JobApplication, id=application_id)
    app.delete()
    return redirect('jobs:applications_dashboard')

def can_post_job(employer):
    limits = get_employer_limits(employer)
    posted_jobs = JobPost.objects.filter(employer=employer).count()
    return posted_jobs < limits['job_limit']

def create_job(request):
    employer = request.user.employer
    if not can_post_job(employer):
        messages.error(request, "You have reached your job posting limit.")
        return redirect('upgrade_page')  # Optional

def consume_user_token(user):
    subscription = Subscription.objects.filter(employer=user, active=True).first()
    if subscription and subscription.consume_token():
        return True
    return False

@login_required
def generate_job_description(request):
    if request.method == 'POST':
        if not has_valid_ai_token(request.user):
            return JsonResponse({'error': 'No AI tokens left.'}, status=403)

        title = request.POST.get('title', '')
        job_role = request.POST.get('role', '')
        industry = request.POST.get('industry', '')

        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)

        # ✅ Demo AI response (ভবিষ্যতে OpenAI বা LLM সংযুক্ত হবে)
        description = f"""
        We are looking for a passionate {title} to join our {industry or 'forward-thinking'} team.
        As a {job_role or title}, you'll be responsible for developing innovative solutions,
        collaborating with cross-functional teams, and driving product excellence.
        """

        # Optional: Token consume করো
        consume_user_token(request.user)

        return JsonResponse({'description': description.strip()})
