import os
import textract
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Resume
from django.core.files.storage import FileSystemStorage
from .utils import (
    extract_email, extract_phone, extract_name,
    extract_skills, extract_experience, extract_education, generate_tags,
    ai_generate_tags,
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
            # ✅ Extract raw text from resume
            text = textract.process(file_path).decode('utf-8')

            # ✅ Clean entire resume text
            cleaned_text = moderate_text(text)

            # ✅ AI-based tag suggestion
            ai_tags = ai_generate_tags(cleaned_text[:1500])

            # combine with basic tags
            tags = ', '.join(set(generate_tags(skills, experience).split(',') + ai_tags.split(',')))


            # ✅ Extract and clean each field
            full_name = moderate_text(extract_name(cleaned_text) or "")
            email = extract_email(cleaned_text)
            phone = extract_phone(cleaned_text)
            skills = moderate_text(extract_skills(cleaned_text) or "")
            experience = moderate_text(extract_experience(cleaned_text) or "")
            education = moderate_text(extract_education(cleaned_text) or "")
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

            if email:
                request.user.email = email
                request.user.save(update_fields=['email'])

            if not jobseeker.address:
                jobseeker.address = "Auto-filled from resume"

            jobseeker.save()

        except Exception as e:
            print("Resume parsing error:", e)

        return redirect('resumes:resume_list')

    return render(request, 'resumes/upload.html')


def resume_list(request):
    resumes = Resume.objects.filter(user=request.user).order_by('-id') 

    paginator = Paginator(resumes, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for resume in page_obj:
        resume.tag_list = [tag.strip() for tag in resume.tags.split(',')] if resume.tags else []

    return render(request, 'resumes/resume_list.html', {'page_obj': page_obj})
