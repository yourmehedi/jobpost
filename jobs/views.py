from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import JobApplication
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from resumes.models import Resume  
from employers.models import EmployerProfile
from moderation.utils import moderate_text
from jobs.utils import calculate_match_score
from subscriptions.models import Subscription
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.urls import reverse
from .forms import JobForm
from django.contrib import messages
from .utils import get_employer_limits
from accounts.models import *
from datetime import datetime
import random
from .models import *
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch

job_desc_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
job_desc_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")

semantic_similarity = pipeline("feature-extraction", model="sentence-transformers/all-MiniLM-L6-v2")

def consume_user_token(user):
    subscription = Subscription.objects.filter(employer=user, active=True).first()
    if subscription and subscription.consume_token():
        return True
    return False

def has_valid_ai_token(user):
    sub = Subscription.objects.filter(employer=user, active=True).first()
    return sub and sub.ai_tokens > 0

@login_required
@require_POST
def generate_job_description(request):
    if not has_valid_ai_token(request.user):
        return JsonResponse({'error': 'No AI tokens available for your plan.'}, status=403)

    title = request.POST.get('title', '').strip()
    role = request.POST.get('role', '').strip()
    industry = request.POST.get('industry', '').strip()

    if not title:
        return JsonResponse({'error': 'Job title is required.'}, status=400)

    prompt = (
        f"Write a detailed, professional job description for a position titled '{title}'. "
        f"The role involves '{role or title}'. Industry: {industry or 'general'}."
    )

    try:
        inputs = job_desc_tokenizer(prompt, return_tensors="pt", truncation=True)
        outputs = job_desc_model.generate(**inputs, max_length=300)
        description = job_desc_tokenizer.decode(outputs[0], skip_special_tokens=True)

        consume_user_token(request.user)
        return JsonResponse({'description': description})

    except torch.cuda.OutOfMemoryError:
        return JsonResponse({'error': 'Server memory full. Try later.'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def post_job(request):
    message = None
    companies = Company.objects.all()

    if request.method == 'POST':
        employer = None
        if not request.user.is_superuser:
            try:
                employer = request.user.employer_profile
            except EmployerProfile.DoesNotExist:
                message = "You must have an employer account to post a job."
                return render(request, 'jobs/post_job.html', {'companies': companies, 'message': message})

        title = request.POST.get('jobTitle')
        company_name = request.POST.get('companyName')
        description = request.POST.get('jobDescription')
        location = request.POST.get('l')
        formatted_address = request.POST.get('formattedAddress')
        salary = request.POST.get('salary')
        skills = request.POST.get('skills')
        tech_stack = ', '.join(request.POST.getlist('stack'))
        vacancies = int(request.POST.get('vacancies') or 1)
        expiry_date_str = request.POST.get('expiry')
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date() if expiry_date_str else None

        job_type = request.POST.get('job_type')
        industry = request.POST.get('industry')
        city = request.POST.get('city')
        country = request.POST.get('country')

        # Moderation
        clean_title = moderate_text(title)
        clean_company_name = moderate_text(company_name)
        clean_description = moderate_text(description)
        clean_skills = moderate_text(skills)

        company, _ = Company.objects.get_or_create(name=clean_company_name)

        Job.objects.create(
            title=clean_title,
            company=company,
            employer=employer,
            description=clean_description,
            location=location,
            formatted_address=formatted_address,
            salary=salary,
            skills=clean_skills,
            tech_stack=tech_stack,
            vacancies=vacancies,
            expiry_date=expiry_date,
            job_type=job_type,
            industry=industry,
            city=city,
            country=country,
            posted_by=request.user
        )

        return redirect('jobs:job_post_success')

    return render(request, 'jobs/post_job.html', {'companies': companies, 'message': message})


def job_post_success(request):
    return render(request, 'jobs/job_success.html')

@login_required
def job_list(request):
    query = request.GET.get('q', '')
    jobs = Job.objects.all().order_by('-posted_at')

    # ✅ Load user's resume (skills + experience)
    user_resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()
    resume_text = ""
    if user_resume:
        resume_text = f"{user_resume.skills or ''} {user_resume.experience or ''}"

    # ✅ HF Semantic Matching
    if resume_text:
        resume_vec = torch.tensor(semantic_similarity(resume_text)).mean(dim=1)
        for job in jobs:
            job_text = f"{job.title} {job.skills} {job.description}"
            job_vec = torch.tensor(semantic_similarity(job_text)).mean(dim=1)
            sim_score = torch.nn.functional.cosine_similarity(resume_vec, job_vec).item()
            job.match_score = round(sim_score * 100, 2)
    else:
        for job in jobs:
            job.match_score = None

    # ✅ Pagination
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'jobs/job_list.html', {'page_obj': page_obj})



@login_required
def employer_job_list(request, user_id):
    employer = get_object_or_404(User, id=user_id)
    jobs = Job.objects.filter(posted_by=employer).order_by('-posted_at')
    return render(request, 'jobs/user_job_list.html', {
        'employer': employer,
        'jobs': jobs,
    })

@login_required
def delete_job(request, job_id): 
    job = get_object_or_404(Job, id=job_id)

    if request.user == job.posted_by or request.user.is_staff:
        job.delete()
        messages.success(request, "Job deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this job.")

    return redirect('employer_job_list', user_id=request.user.id)

def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.user != job.posted_by and not request.user.is_staff:
        messages.error(request, "You are not authorized to edit this job.")
        return redirect('jobs:employer_job_list', user_id=request.user.id)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully.")
            return redirect('jobs:employer_job_list', user_id=request.user.id)
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/edit_job.html', {
        'form': form,
        'job': job
    })

@require_POST
@login_required
def save_job(request):
    job_id = request.POST.get('job_id')
    print("Received job_id:", job_id)  # Debug

    if not job_id or not job_id.isdigit():
        return HttpResponseBadRequest("Invalid job ID.")

    job = get_object_or_404(Job, id=job_id)

    try:
        jobseeker = Jobseeker.objects.get(user=request.user)
    except Jobseeker.DoesNotExist:
        messages.error(request, "You are not a jobseeker.")
        return redirect('jobs:job_detail', job_id=job.id)

    # Job Save/Unsave Logic
    saved, created = SavedJob.objects.get_or_create(jobseeker=jobseeker, job=job)

    if created:
        messages.success(request, "Job saved successfully.")
    else:
        saved.delete()
        messages.info(request, "Job removed from saved list.")

    return redirect('jobs:job_detail', job_id=job.id)

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    saved_jobs = []
    if request.user.is_authenticated:
        try:
            jobseeker = Jobseeker.objects.get(user=request.user)
            saved_jobs = SavedJob.objects.filter(jobseeker=jobseeker).values_list('job_id', flat=True)
        except Jobseeker.DoesNotExist:
            saved_jobs = []

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'saved_jobs': saved_jobs,
    })

def more_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobs/more_detail.html', {'job': job})

@login_required
def saved_jobs_list(request):
    jobseeker = request.user.jobseeker_profile  
    saved_jobs = SavedJob.objects.filter(jobseeker=jobseeker).select_related('job').order_by('-saved_at')

    return render(request, 'jobs/saved_jobs.html', {
        'saved_jobs': saved_jobs
    })

@login_required
def unsave_job(request, job_id):
    jobseeker = request.user.jobseeker_profile
    saved_job = get_object_or_404(SavedJob, jobseeker=jobseeker, job__id=job_id)
    saved_job.delete()
    messages.info(request, "Job removed from saved list.")
    return redirect('jobs:saved_jobs_list')

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

def consume_user_token(user):
    subscription = Subscription.objects.filter(employer=user, active=True).first()
    if subscription and subscription.consume_token():
        return True
    return False