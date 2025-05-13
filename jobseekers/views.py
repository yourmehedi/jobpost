from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from jobseekers.models import Jobseeker, AdditionalInfo
from datetime import datetime

@login_required
def profile_builder(request):
    user = request.user

    try:
        jobseeker = user.jobseeker
    except Jobseeker.DoesNotExist:
        jobseeker = None  # আমরা POST-এর সময় তৈরি করব

    if request.method == 'POST':
        if not jobseeker:
            jobseeker = Jobseeker(user=user)

        # প্রোফাইল তথ্য সংরক্ষণ
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

        # তারিখ সঠিক ফর্ম্যাটে রূপান্তর
        if isinstance(jobseeker.date_of_birth, str):
            try:
                jobseeker.date_of_birth = datetime.strptime(jobseeker.date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                pass  # ভুল ডেট থাকলে save এর আগে error handle করুন

        jobseeker.save()

        # অতিরিক্ত তথ্য
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
