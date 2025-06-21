from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from .forms import JobForm
import random
from .models import *
from django.contrib import messages
from .utils import get_employer_limits
from accounts.models import *
from datetime import datetime
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

def has_valid_ai_token(user):
    sub = Subscription.objects.filter(employer=user, active=True).first()
    return sub and sub.ai_tokens > 0

@login_required
def post_job(request):
    message = None
    companies = Company.objects.all()

    if request.method == 'POST':
        employer = None

        if request.user.is_superuser:
            # Allow superuser to post without EmployerProfile
            employer = None
        else:
            try:
                employer = request.user.employer_profile
            except EmployerProfile.DoesNotExist:
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

        # ✅ Clean text
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
            employer=employer,  # None for superuser
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
    location = request.GET.get('location', '')
    company = request.GET.get('company', '')
    job_type = request.GET.get('job_type', '')
    experience = request.GET.get('experience', '')
    min_salary = request.GET.get('min_salary')
    max_salary = request.GET.get('max_salary')

    jobs = Job.objects.all()

    # Apply search filter
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company__name__icontains=query) |
            Q(description__icontains=query)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if company:
        jobs = jobs.filter(company__name__icontains=company)

    if job_type:
        jobs = jobs.filter(job_type__iexact=job_type)

    if experience:
        jobs = jobs.filter(experience_level__iexact=experience)

    if min_salary:
        jobs = jobs.filter(salary__gte=min_salary)

    if max_salary:
        jobs = jobs.filter(salary__lte=max_salary)

    jobs = jobs.order_by('-posted_at')

    # Pagination
    paginator = Paginator(jobs, 1)  # Change 5 to your desired number per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'jobs/job_list.html', {
        'page_obj': page_obj,
        'jobs': jobs,  # Optional — আপনি চাইলে শুধু `page_obj` ব্যবহার করলেও চলবে
    })


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

    # ✅ CustomUser থেকে Jobseeker instance বের করি
    try:
        jobseeker = Jobseeker.objects.get(user=request.user)
    except Jobseeker.DoesNotExist:
        messages.error(request, "You are not a jobseeker.")
        return redirect('jobs:job_detail', job_id=job.id)

    # ✅ Job Save/Unsave Logic
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
    jobseeker = request.user.jobseeker_profile  # যেহেতু Jobseeker মডেলে OneToOneField আছে
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
