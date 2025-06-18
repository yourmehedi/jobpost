from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import EmployerRegistrationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model, authenticate, login
from employers.models import EmployerProfile
from subscriptions.models import *
from management.models import Employer
from jobs.models import Job
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
User = get_user_model()
  
@login_required
def home(request):
    print(request.user)
    return render(request, 'management/home.html')

def employer_register(request):
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            if User.objects.filter(username=username).exists():
                form.add_error('username', 'This username is already taken.')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )

                Employer.objects.create(
                    user=user,
                    company_name=form.cleaned_data['company_name'],
                    company_website=form.cleaned_data['company_website'],
                    employer_type=form.cleaned_data['employer_type'],
                    license_file=form.cleaned_data.get('license_file')
                )

                return redirect('management:registration_success')
    else:
        form = EmployerRegistrationForm()
    return render(request, 'management/employer_register.html', {'form': form})

def registration_success(request):
    return render(request, 'management/success.html')

@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def dashboard_home(request):
    return render(request, 'management/dashboard_home.html')


def superuser_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('management:dashboard')  
            else:
                messages.error(request, 'you are not superuser!')
        else:
            messages.error(request, 'Username and password wrong!')

    return render(request, 'management/superuser_login.html')

@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def user_approval(request):
    users = User.objects.filter(is_active=False)
    return render(request, 'management/user_approval.html', {'users': users})

@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def employer_verification(request):
    employers = EmployerProfile.objects.filter(is_approved=False)
    return render(request, 'management/employer_verification.html', {'employers': employers})

@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def verify_employer(request, id):
    employer = get_object_or_404(EmployerProfile, id=id)
    employer.is_approved = True
    employer.save()

    # Approve user account too
    employer.user.is_approved = True
    employer.user.save()

    return redirect('management:employer_verification')

@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def job_monitoring(request):
    jobs = Job.objects.all()
    
    return render(request, 'management/job_monitoring.html', {'jobs': jobs})



@user_passes_test(lambda u: u.is_superuser, login_url='management:superuser_login')
def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return redirect('management:user_approval')

def review_user_jobs(request, employer_id):
    employer = get_object_or_404(Employer, id=employer_id)
    jobs = Job.objects.filter(employer=employer)
    return render(request, 'management/review_user_jobs.html', {'employer': employer, 'jobs': jobs})

def toggle_job_status(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if job.status == 'active':
        job.status = 'closed'
    else:
        job.status = 'active'
    job.save()
    return redirect('management:job_monitoring')

def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    job.delete()
    return redirect('management:job_monitoring')

def ai_token_usage(request):
    premium_users = Subscription.objects.select_related('user', 'plan').filter(
        active=True,
        plan__has_ai_access=True
    )
    return render(request, 'management/ai_token_usage.html', {
        'premium_users': premium_users
    })


def subscription_history(request):
    subscriptions = Subscription.objects.select_related('plan').filter(user=request.user).order_by('-start_date')  # আগে ছিল employer
    return render(request, 'management/subscription_history.html', {
        'subscriptions': subscriptions,
    })