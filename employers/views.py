from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import EmployerRegistrationForm, EmployerDocumentForm, EmployerProfile, EmployerProfileForm
from .models import *
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from subscriptions.models import Subscription
from django.contrib.auth import update_session_auth_hash


User = get_user_model()  

def has_valid_ai_token(user):
    sub = Subscription.objects.filter(employer=user, active=True).first()
    return sub and sub.ai_tokens > 0


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

@login_required
def edit_employer_profile(request):
    profile = get_object_or_404(EmployerProfile, user=request.user)

    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('employers:dashboard')  # আপনার ড্যাশবোর্ড URL নাম অনুযায়ী ঠিক করুন
    else:
        form = EmployerProfileForm(instance=profile)

    return render(request, 'employers/edit_profile.html', {'form': form})

@login_required
def employer_settings(request):
    profile = get_object_or_404(EmployerProfile, user=request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            settings_form = EmployerProfileForm(request.POST, instance=profile)
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('employers:settings')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect('employers:settings')
            else:
                messages.error(request, "Please correct the errors below.")

        elif 'upload_document' in request.POST:
            document_form = EmployerDocumentForm(request.POST, request.FILES, instance=profile)
            if document_form.is_valid():
                document_form.save()
                messages.success(request, "Document uploaded successfully.")
                return redirect('employers:settings')

    else:
        settings_form = EmployerProfileForm(instance=profile)
        password_form = PasswordChangeForm(user=request.user)
        document_form = EmployerDocumentForm(instance=profile)

    return render(request, 'employers/settings.html', {
        'settings_form': settings_form,
        'password_form': password_form,
        'document_form': document_form,
    })