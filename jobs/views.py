from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Company, Job, JobPost, JobApplication
from django.contrib import messages
from .utils import get_employer_limits
from accounts.models import Employer
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from .models import JobApplication

def post_job(request):
    message = None
    companies = Company.objects.all()

    if request.method == 'POST':
        try:
            title = request.POST.get('jobTitle')
            company_name = request.POST.get('companyName')
            description = request.POST.get('jobDescription')
            location = request.POST.get('l')
            formatted_address = request.POST.get('formattedAddress')
            salary = request.POST.get('salary')
            is_email_protected = request.POST.get('anonymizeEmail') == 'on'

            skills = request.POST.get('skills')
            tech_stack = ', '.join(request.POST.getlist('stack'))

            # Convert string to int safely
            try:
                vacancies = int(request.POST.get('vacancies'))
            except (TypeError, ValueError):
                vacancies = 1

            # Convert string to date safely
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

            # Validate required fields
            required_fields = [title, company_name, description, location]
            if not all(required_fields):
                message = "Please fill in all required fields."
            else:
                company, created = Company.objects.get_or_create(name=company_name)

                Job.objects.create(
                    title=title,
                    company=company,
                    description=description,
                    location=location,
                    formatted_address=formatted_address,
                    salary=salary,
                    is_email_protected=is_email_protected,
                    skills=skills,
                    tech_stack=tech_stack,
                    vacancies=vacancies,
                    expiry_date=expiry_date,
                    valid_passport=valid_passport,
                    principal=principal,
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

                return redirect('jobs:job_list')

        except Exception as e:
            message = f"An error occurred: {e}"

    context = {
        'companies': companies,
        'message': message,
    }
    return render(request, 'jobs/post_job.html', context)

@login_required(login_url='accounts:login') 
def job_list(request):
    jobs = Job.objects.select_related('company').order_by('-posted_at')

    for job in jobs:
        job.skill_list = job.skills.split(",") if job.skills else []
        job.perk_list = job.perks.split(",") if job.perks else []

    return render(request, 'jobs/job_list.html', {'jobs': jobs})

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobs/job_detail.html', {'job': job})

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
def job_applications_list(request):
    applications = JobApplication.objects.all().order_by('-applied_at')
    return render(request, 'jobs/applications_dashboard.html', {'applications': applications})

@staff_member_required
def reply_application(request, application_id):
    app = get_object_or_404(JobApplication, id=application_id)

    if request.method == 'POST':
        app.reply = request.POST.get('reply')
        app.save()
        return redirect('jobs:applications_dashboard')

    return render(request, 'jobs/reply_application.html', {'application': app})

@staff_member_required
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


