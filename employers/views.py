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
    try:
        existing = EmployerProfile.objects.get(user=request.user)
        return redirect('dashboard')  
    except EmployerProfile.DoesNotExist:
        pass

    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            employer = form.save(commit=False)
            employer.user = request.user
            employer.save()
            return redirect('dashboard')
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
