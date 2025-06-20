import os
import fitz  # PyMuPDF
import textract
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from .models import Resume
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
        if file_ext not in ALLOWED_EXTENSIONS:
            messages.error(request, "Invalid file type. Please upload a PDF, DOC, or DOCX file.")
            return redirect('resumes:upload_resume')

        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)

        try:
            # ✅ Use PyMuPDF for PDF, textract otherwise
            if file_ext == '.pdf':
                text = extract_pdf_text(file_path)
            else:
                text = textract.process(file_path).decode('utf-8')

            cleaned_text = moderate_text(text)

            full_name = moderate_text(extract_name(cleaned_text) or "")
            email = extract_email(cleaned_text)
            phone = extract_phone(cleaned_text)
            skills = moderate_text(extract_skills(cleaned_text) or "")
            experience = moderate_text(extract_experience(cleaned_text) or "")
            education = moderate_text(extract_education(cleaned_text) or "")

            # ✅ Generate tags (combined basic + AI)
            ai_tags = ai_generate_tags(cleaned_text[:1500])
            tags = ', '.join(set(generate_tags(skills, experience).split(',') + ai_tags.split(',')))

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

            messages.success(request, "Resume uploaded and processed successfully.")
            return redirect('resumes:resume_success')

        
        except Exception as e:
            print("Resume parsing error:", e)
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

