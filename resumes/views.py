import os
import fitz  
import textract
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from .models import Resume
from django.contrib.auth.models import User
from .utils import (
    extract_email, extract_phone, extract_name,
    extract_skills, extract_experience, extract_education, generate_tags,
    ai_generate_tags,
)
from jobseekers.models import Jobseeker
from moderation.utils import moderate_text  # ✅ Import moderation

# ✅ Allowed file extensions
ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx']

def extract_pdf_text(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text() 
    return text
@login_required
def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        uploaded_file = request.FILES['resume']
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()

        # ✅ Validate file type
        if file_ext not in ['.pdf', '.doc', '.docx']:
            messages.error(request, "Invalid file type. Please upload a PDF, DOC, or DOCX file.")
            return redirect('resumes:upload_resume')

        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)

        try:
            # ✅ Extract text
            if file_ext == '.pdf':
                text = extract_pdf_text(file_path)
            else:
                text = textract.process(file_path).decode('utf-8')

            print("🧾 Raw Extracted Text:\n", text[:1000])  # Debug

            # ✅ Apply moderation (optional)
            try:
                cleaned_text = moderate_text(text)
            except Exception as e:
                print("⚠️ moderate_text failed, using raw text:", e)
                cleaned_text = text

            # ✅ Extract individual fields
            full_name = extract_name(cleaned_text) or ""
            email = extract_email(cleaned_text)
            phone = extract_phone(cleaned_text)
            skills = extract_skills(cleaned_text) or ""
            experience = extract_experience(cleaned_text) or ""
            education = extract_education(cleaned_text) or ""

            # ✅ Print for debug
            print("✅ Extracted Data:")
            print("Full Name:", full_name)
            print("Email:", email)
            print("Phone:", phone)
            print("Skills:", skills)
            print("Experience:", experience)
            print("Education:", education)

            # ✅ Generate tags
            ai_tags = ai_generate_tags(cleaned_text[:1500])
            tags = ', '.join(set(generate_tags(skills, experience).split(',') + ai_tags.split(',')))

            # ✅ Save to Resume model
            Resume.objects.create(
                user=request.user,
                posted_by=request.user,
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
            jobseeker, _ = Jobseeker.objects.get_or_create(user=request.user)

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

            messages.success(request, "✅ Resume uploaded and processed successfully.")
            return redirect('resumes:resume_success')

        except Exception as e:
            print("❌ Resume parsing error:", e)
            messages.error(request, "There was an error processing your resume.")

        return redirect('resumes:resume_list')

    return render(request, 'resumes/upload.html')


def resume_success(request):
    return render(request, 'resumes/seccess.html')

def resume_list(request):
    resumes = Resume.objects.filter(user=request.user).order_by('-id')

    paginator = Paginator(resumes, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for resume in page_obj:
        resume.tag_list = [tag.strip() for tag in resume.tags.split(',')] if resume.tags else []
    
    return render(request, 'resumes/resume_list.html', {'page_obj': page_obj})

@login_required
def jobseeker_resume_list(request, user_id):
    resumes = Resume.objects.filter(posted_by__id=user_id).order_by('-uploaded_at')
    return render(request, 'resumes/jobseeker_resume_list.html', {
        'resumes': resumes
    })


@login_required
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)

    if request.user == resume.posted_by or request.user.is_staff:
        resume.delete()
        messages.success(request, "Resume deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this resume.")

    return redirect('resumes:jobseeker_resume_list', user_id=request.user.id)
