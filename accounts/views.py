# accounts/views.py

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Employer
from django.db import transaction
from jobseekers.models import Jobseeker
from management.models import Employer


User = get_user_model()

@transaction.atomic
def register(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')  # 'jobseeker' or 'employer'

        if not all([username, email, password, confirm_password, user_type]):
            messages.error(request, 'All fields are required.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type=user_type
            )

            # Create Employer or Jobseeker profile
            if user_type == 'employer':
                employer_type = request.POST.get('employer_type')  # e.g. 'direct'
                company_name = request.POST.get('company_name')
                tin = request.POST.get('tin')

                Employer.objects.create(
                    user=user,
                    employer_type=employer_type,
                    company_name=company_name,
                    tin=tin
                )

            elif user_type == 'jobseeker':
                Jobseeker.objects.create(user=user, full_name=username)

            messages.success(request, 'Registration successful! Please login.')
            return redirect('accounts:login')

    return render(request, 'accounts/register.html')

def login_view(request):
    message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)

                # ✅ Superuser check
                if user.is_superuser or user.user_type == 'superadmin':
                    return redirect('management:dashboard')

                # ✅ Employer check
                elif user.user_type == 'employer':  # ✅ fixed
                    return redirect('employers:dashboard')

                # ✅ Jobseeker check
                elif user.user_type == 'jobseeker':  # ✅ fixed
                    return redirect('jobseeker:dashboard')

                else:
                    message = 'Unknown user type.'
            else:
                message = 'Invalid username or password'
        else:
            message = 'Username and password are required'

    return render(request, 'accounts/login.html', {'message': message})


def user_profile(request):
    return render(request, 'accounts/profile.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')
