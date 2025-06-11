from django.shortcuts import render, redirect
from .forms import EmployerRegistrationForm
from .models import EmployerProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from subscriptions.models import Subscription

User = get_user_model()  

def has_valid_ai_token(user):
    sub = Subscription.objects.filter(employer=user, active=True).first()
    return sub and sub.ai_tokens > 0



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

                EmployerProfile.objects.create(
                    user=user,
                    company_name=form.cleaned_data['company_name'],
                    company_website=form.cleaned_data['company_website'],
                    employer_type=form.cleaned_data['employer_type'],
                    license_file=form.cleaned_data.get('license_file')
                )

                return redirect('management:registration_success')
    else:
        form = EmployerRegistrationForm()
    return render(request, 'employers/employer_register.html', {'form': form})

@login_required
def employer_dashboard(request):
    user = request.user
    profile = EmployerProfile.objects.filter(user=user).first()
    subscription = Subscription.objects.filter(employer=user, active=True).first()

    context = {
        'profile': profile,
        'subscription': subscription,
    }

    return render(request, 'employers/employer_dashboard.html', context)
