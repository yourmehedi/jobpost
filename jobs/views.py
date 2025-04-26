from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Company, Job, JobPost
from django.contrib import messages
from .utils import get_employer_limits
from accounts.models import Employer

@login_required
def post_job(request):
    message = None
    companies = Company.objects.all()

    if request.method == 'POST':
        title = request.POST.get('jobTitle')
        company_name = request.POST.get('companyName')
        description = request.POST.get('jobDescription')
        location = request.POST.get('l')
        formatted_address = request.POST.get('formattedAddress')
        salary = request.POST.get('salary')
        is_email_protected = request.POST.get('anonymizeEmail') == 'on'

        if not all([title, company_name, description, location]):
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
                posted_by=request.user  
            )
            return redirect('jobs:job_list')

    context = {
        'companies': companies,
        'message': message,
    }
    return render(request, 'jobs/post_job.html', context)

@login_required(login_url='accounts:login') 
def job_list(request):
    jobs = Job.objects.select_related('company').order_by('-posted_at')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})



def can_post_job(employer):
    limits = get_employer_limits(employer)
    posted_jobs = JobPost.objects.filter(employer=employer).count()
    return posted_jobs < limits['job_limit']


def create_job(request):
    employer = request.user.employer
    if not can_post_job(employer):
        messages.error(request, "You have reached your job posting limit.")
        return redirect('upgrade_page')  # Optional


