import os
import textract
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Resume
from django.core.files.storage import FileSystemStorage
from .utils import (
    extract_email, extract_phone, extract_name,
    extract_skills, extract_experience, extract_education, generate_tags
)
from jobseekers.models import Jobseeker
from datetime import datetime
from moderation.utils import moderate_text  # ✅ Import moderation

@login_required
def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        uploaded_file = request.FILES['resume']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)

        try:
            # ✅ Resume text extract
            text = textract.process(file_path).decode('utf-8')

            # ✅ Run moderation filter before extraction
            text = moderate_text(text)

            # ✅ Extracted data from AI/parser
            full_name = extract_name(text)
            email = extract_email(text)
            phone = extract_phone(text)
            skills = extract_skills(text)
            experience = extract_experience(text)
            education = extract_education(text)
            tags = generate_tags(skills, experience)

            # ✅ Save to Resume model
            Resume.objects.create(
                user=request.user,
                file=uploaded_file,
                full_name=full_name,
                email=email,
                phone=phone,
                skills=skills,
                experience=experience,
                education=education,
                tags=tags
            )

            # ✅ Auto-fill Jobseeker profile
            jobseeker, created = Jobseeker.objects.get_or_create(user=request.user)

            if full_name:
                jobseeker.full_name = full_name

            if phone:
                jobseeker.contact_number = phone

            # Email update (to User model directly)
            if email:
                request.user.email = email
                request.user.save(update_fields=['email'])

            # Default fallback if address isn't parsed
            if not jobseeker.address:
                jobseeker.address = "Auto-filled from resume"

            jobseeker.save()

        except Exception as e:
            print("Resume parsing error:", e)

        return redirect('resumes:resume_list')

    return render(request, 'resumes/upload.html')

def resume_list(request):

    return render(request, 'resumes/resume_list.html')