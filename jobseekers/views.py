from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from jobseekers.models import Jobseeker, AdditionalInfo
from jobs.utils import calculate_match_score
from .forms import JobseekerSettingsForm, PasswordChangeForm, DocumentUploadForm
from django.contrib.auth import update_session_auth_hash
from datetime import datetime
from jobs.models import *
from resumes.models import *
from .forms import *

@login_required
def profile_builder(request):
    user = request.user

    try:
        jobseeker = request.user.jobseeker_profile
    except Jobseeker.DoesNotExist:
        jobseeker = None  

    if request.method == 'POST':
        if not jobseeker:
            jobseeker = Jobseeker(user=user)

        jobseeker.full_name = request.POST.get('full_name')
        jobseeker.date_of_birth = request.POST.get('dob')
        jobseeker.gender = request.POST.get('gender')
        jobseeker.contact_number = request.POST.get('contact')
        jobseeker.address = request.POST.get('address')
        jobseeker.job_type_preference = request.POST.get('job_type')
        jobseeker.preferred_country = request.POST.get('preferred_country')
        jobseeker.preferred_city = request.POST.get('preferred_city')
        jobseeker.passport_number = request.POST.get('passport')
        jobseeker.national_id = request.POST.get('nid')

        if request.FILES.get('document'):
            jobseeker.document_upload = request.FILES['document']

        if isinstance(jobseeker.date_of_birth, str):
            try:
                jobseeker.date_of_birth = datetime.strptime(jobseeker.date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                pass 

        jobseeker.save()

        about = request.POST.get('about_me')
        achievements = request.POST.get('achievements')
        hobbies = request.POST.get('hobbies')

        AdditionalInfo.objects.update_or_create(
            jobseeker=jobseeker,
            defaults={
                'about_me': about,
                'achievements': achievements,
                'hobbies': hobbies
            }
        )

        return redirect('jobseeker:profile_view')

    return render(request, 'jobseekers/profile_builder.html', {'jobseeker': jobseeker})

@login_required
def profile_view(request):
    print(request.user)
    try:
        jobseeker = request.user.jobseeker_profile
    except:
        jobseeker = None
    
    additional_info = None
    if jobseeker:
        additional_info = getattr(jobseeker, 'additionalinfo', None)

    return render(request, 'jobseekers/profile_view.html', {
        'jobseeker': jobseeker,
        'additional_info': additional_info
    })

@login_required
def saved_jobs(request):
    saved = SavedJob.objects.filter(jobseeker=request.user).select_related('job')
    return render(request, 'jobs/saved_jobs.html', {'saved_jobs': saved})



# @login_required
# def edit_profile(request):
#     jobseeker = request.user.jobseeker_profile  # Ensure related_name is used
#     if request.method == 'POST':
#         form = JobseekerForm(request.POST, instance=jobseeker)
#         if form.is_valid():
#             form.save()
#             return redirect('jobseeker:profile_view')  # Replace with your profile view URL name
#     else:
#         form = JobseekerForm(instance=jobseeker)
#     return render(request, 'jobseekers/edit_profile.html', {'form': form})

@login_required
def account_settings(request):
    jobseeker = request.user.jobseeker_profile

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            settings_form = JobseekerSettingsForm(request.POST, request.FILES, instance=jobseeker)
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, 'Profile updated successfully!')
            else:
                messages.error(request, 'Please correct the errors in your profile form.')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!')
            else:
                messages.error(request, 'Please correct the errors in your password form.')

        elif 'upload_document' in request.POST:
            document_form = DocumentUploadForm(request.POST, request.FILES, instance=jobseeker)
            if document_form.is_valid():
                document_form.save()
                messages.success(request, 'Document updated!')
            else:
                messages.error(request, 'Please correct the errors in your document upload form.')

        return redirect('jobseeker:account_settings')

    else:
        settings_form = JobseekerSettingsForm(instance=jobseeker)
        password_form = PasswordChangeForm(user=request.user)
        document_form = DocumentUploadForm(instance=jobseeker)

    context = {
        'settings_form': settings_form,
        'password_form': password_form,
        'document_form': document_form,
    }
    return render(request, 'jobseekers/settings.html', context)

@login_required
def dashboard(request):
    try:
        jobseeker = request.user.jobseeker_profile
    except Jobseeker.DoesNotExist:
        messages.warning(request, "Please complete your profile first.")
        return redirect('jobseeker:profile_builder')

    resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()
    resume_skills = resume.skills if resume else ''
    resume_exp = resume.experience if resume else ''
    country = jobseeker.preferred_country or ''
    city = jobseeker.preferred_city or ''

    jobs = Job.objects.filter(status='active').order_by('-posted_at')

    recommended = []
    for job in jobs:
        score = calculate_match_score(job.skills, resume_skills, resume_exp)
        if country.lower() in (job.country or '').lower():
            score += 0.1
        if city.lower() in (job.city or '').lower():
            score += 0.1
        if score >= 0.3:
            job.match_score = round(score * 100)
            recommended.append(job)

    recommended = sorted(recommended, key=lambda j: j.match_score, reverse=True)

    return render(request, 'jobseekers/dashboard.html', {
        'jobseeker': jobseeker,
        'recommended_jobs': recommended[:6]  # Show top 6
    })



@login_required
def telegram_settings(request):
    user = request.user

    if not user.is_jobseeker:
        messages.error(request, "Only jobseekers can access this page.")
        return redirect('jobseeker:dashboard')  

    if request.method == 'POST':
        telegram_chat_id = request.POST.get('telegram_chat_id')
        telegram_enabled = bool(request.POST.get('telegram_enabled'))

        user.telegram_chat_id = telegram_chat_id
        user.telegram_enabled = telegram_enabled
        user.save()

        messages.success(request, "Telegram settings updated.")
        return redirect('jobseeker:telegram_settings')

    return render(request, 'jobseekers/telegram_settings.html', {
        'user': user
    })