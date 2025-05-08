from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import EmployerRegistrationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from employers.models import EmployerProfile
from jobs.models import Job



def home(request):
    return render(request, 'management/home.html')


def employer_register(request):
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/employer/success/')
    else:
        form = EmployerRegistrationForm()
    return render(request, 'management/employer_register.html', {'form': form})


def registration_success(request):
    return render(request, 'management/success.html')

User = get_user_model()

def dashboard_home(request):
    return render(request, 'management/dashboard_home.html')

def user_approval(request):
    users = User.objects.filter(is_active=False)
    return render(request, 'management/user_approval.html', {'users': users})

def employer_verification(request):
    employers = EmployerProfile.objects.filter(license_verified=False)
    return render(request, 'management/employer_verification.html', {'employers': employers})

def job_monitoring(request):
    jobs = Job.objects.all()
    return render(request, 'management/job_monitoring.html', {'jobs': jobs})


def approve_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return redirect('management:user_approval')
