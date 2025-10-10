# resumes/views.py
import os
import fitz  
import textract
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from .models import Resume
from jobseekers.models import Jobseeker
from moderation.utils import moderate_text
from .utils import (
    extract_email, extract_phone, extract_name,
    extract_skills, extract_experience, extract_education,
    generate_tags, ai_generate_tags
)

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
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            messages.error(request, "Invalid file type.")
            return redirect('resumes:upload_resume')

        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        path = fs.path(filename)

        try:
            text = extract_pdf_text(path) if ext == '.pdf' else textract.process(path).decode('utf-8')
            cleaned_text = moderate_text(text) if 'moderate_text' in globals() else text

            full_name = extract_name(cleaned_text) or ""
            email = extract_email(cleaned_text) or ""
            phone = extract_phone(cleaned_text) or ""
            skills = extract_skills(cleaned_text) or ""
            experience = extract_experience(cleaned_text) or ""
            education = extract_education(cleaned_text) or ""

            base_tags = generate_tags(skills, experience)
            ai_tags = ai_generate_tags(cleaned_text)
            combined = ', '.join([t.strip() for t in (base_tags + ',' + ai_tags).split(',') if t.strip()])
            combined = ', '.join(sorted(set([t.strip() for t in combined.split(',') if t.strip()])))

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
                tags=combined
            )

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

            messages.success(request, "Resume uploaded & processed.")
            return redirect('resumes:resume_success')

        except Exception as e:
            print("Resume processing error:", e)
            messages.error(request, "Error processing resume.")
            return redirect('resumes:resume_list')

    return render(request, 'resumes/upload.html')


# def ai_generate_tags_hf(text):
#     """Generate smart tags using Hugging Face zero-shot classifier"""
#     candidate_labels = [
#         "Python", "Django", "Machine Learning", "Data Science", "React", "Project Management",
#         "Marketing", "Finance", "Education", "Engineering", "Software Development",
#         "Customer Support", "Sales", "Design", "Human Resources", "Remote Work"
#     ]

#     try:
#         result = tag_generator(text[:1000], candidate_labels)
#         top_labels = [label for label, score in zip(result['labels'], result['scores']) if score > 0.35]
#         return ', '.join(top_labels)
#     except Exception as e:
#         print("⚠️ AI Tagging failed:", e)
#         return ""


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
    return render(request, 'resumes/jobseeker_resume_list.html', {'resumes': resumes})


@login_required
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)

    if request.user == resume.posted_by or request.user.is_staff:
        resume.delete()
        messages.success(request, "Resume deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this resume.")

    return redirect('resumes:jobseeker_resume_list', user_id=request.user.id)
