# # ai_engine/views.py

# from django.http import JsonResponse
# from django.shortcuts import redirect, render
# from django.views.decorators.csrf import csrf_exempt
# from django.conf import settings
# from subscriptions.models import Subscription
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.http import require_POST
# from django.contrib import messages

# # ✅ Hugging Face Imports
# from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
# import torch

# # 🔹 Load lightweight models once
# resume_ner = pipeline("ner", model="dslim/bert-base-NER", grouped_entities=True)
# text_gen_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
# text_gen_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")

# # ✅ Helper: consume AI token
# def consume_user_token(user):
#     subscription = Subscription.objects.filter(employer=user, active=True).first()
#     if subscription and subscription.consume_token():
#         return True
#     return False


# # ✅ Resume Parser (HF version)
# @login_required
# def resume_parser(request):
#     # ✅ Check AI access (same as before)
#     if not Subscription.objects.filter(employer=request.user, active=True, ai_tokens__gt=0).exists():
#         messages.error(request, "This is a premium feature. Please upgrade your plan.")
#         return redirect('subscriptions:plan_list')

#     parsed_data = None

#     if request.method == 'POST':
#         resume_text = request.POST.get('resume_text', '')
#         if resume_text.strip():
#             try:
#                 # ✅ Use Hugging Face NER to extract info
#                 entities = resume_ner(resume_text[:3000])
#                 extracted = {"Name": "", "Email": "", "Phone": "", "Skills": "", "Experience": "", "Education": ""}

#                 # Extract PERSON
#                 for ent in entities:
#                     if ent['entity_group'] == 'PER' and not extracted["Name"]:
#                         extracted["Name"] = ent['word']

#                 # Simple regex for email / phone
#                 import re
#                 email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
#                 phone = re.search(r'(\+?\d[\d\s\-\(\)]{6,}\d)', resume_text)

#                 extracted["Email"] = email.group(0) if email else ""
#                 extracted["Phone"] = phone.group(0) if phone else ""

#                 # ✅ Simple heuristic-based sections
#                 lower_text = resume_text.lower()
#                 if "education" in lower_text:
#                     extracted["Education"] = resume_text.split("education", 1)[-1][:300]
#                 if "experience" in lower_text:
#                     extracted["Experience"] = resume_text.split("experience", 1)[-1][:300]
#                 if "skills" in lower_text:
#                     extracted["Skills"] = resume_text.split("skills", 1)[-1][:200]

#                 parsed_data = "\n".join([f"{k}: {v}" for k, v in extracted.items() if v])

#                 consume_user_token(request.user)

#             except Exception as e:
#                 messages.error(request, f"Something went wrong: {str(e)}")

#         else:
#             messages.error(request, "Please enter resume text.")

#     return render(request, 'ai_engine/resume_parser.html', {
#         'parsed_data': parsed_data
#     })


# # ✅ Job Description Generator (HF version)
# @login_required
# @require_POST
# def generate_job_description(request):
#     # ✅ Check subscription and tokens
#     if not Subscription.objects.filter(user=request.user, active=True, ai_tokens__gt=0).exists():
#         return JsonResponse({'error': 'AI access is not available for your plan.'}, status=403)

#     title = request.POST.get('title', '').strip()
#     role = request.POST.get('role', '').strip()
#     industry = request.POST.get('industry', '').strip()

#     if not title:
#         return JsonResponse({'error': 'Job title is required.'}, status=400)

#     try:
#         prompt = (
#             f"Write a professional and detailed job description for a position titled '{title}'. "
#             f"The role of the candidate will be '{role or title}'. "
#             f"Industry: {industry or 'general'}."
#         )

#         # ✅ Hugging Face generation
#         inputs = text_gen_tokenizer(prompt, return_tensors="pt", truncation=True)
#         outputs = text_gen_model.generate(**inputs, max_length=250)
#         description = text_gen_tokenizer.decode(outputs[0], skip_special_tokens=True)

#         consume_user_token(request.user)

#         return JsonResponse({'description': description})

#     except torch.cuda.OutOfMemoryError:
#         return JsonResponse({'error': 'Server is out of memory. Try again later.'}, status=500)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


# ai_engine/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from subscriptions.models import Subscription

# Hugging Face
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch

# Load once (choose small model for CPU; change to larger if GPU available)
# For resume parsing we use a text2text model (flan-t5-small)
try:
    rp_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
    rp_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
    rp_pipe = pipeline("text2text-generation", model=rp_model, tokenizer=rp_tokenizer)
except Exception as e:
    print("⚠️ ai_engine: resume parser model load error:", e)
    rp_pipe = None

# job description generation can reuse flan-t5-small
try:
    jd_tokenizer = rp_tokenizer
    jd_model = rp_model
    jd_pipe = rp_pipe
except Exception as e:
    jd_pipe = None

def has_ai_access(user):
    return Subscription.objects.filter(employer=user, active=True, ai_tokens__gt=0).exists()

def consume_user_token(user):
    subscription = Subscription.objects.filter(employer=user, active=True).first()
    if subscription and subscription.consume_token():
        return True
    return False

@login_required
def resume_parser(request):
    if not has_ai_access(request.user):
        messages.error(request, "This is a premium feature. Please upgrade your plan.")
        return redirect('subscriptions:plan_list')

    parsed_data = None
    if request.method == 'POST':
        resume_text = request.POST.get('resume_text', '').strip()
        if not resume_text:
            messages.error(request, "Please enter resume text.")
            return redirect('ai_engine:resume_parser')

        if not rp_pipe:
            messages.error(request, "Resume parser model not available on server.")
            return redirect('ai_engine:resume_parser')

        try:
            prompt = (
                "Extract structured information from the following resume text as bullet points. "
                "Return Name:, Email:, Phone:, Skills:, Experience:, Education: each on its own line.\n\n"
                f"{resume_text[:4000]}"
            )
            out = rp_pipe(prompt, max_length=256, do_sample=False)
            parsed_data = out[0].get('generated_text', '').strip()

            # consume token
            consume_user_token(request.user)

        except Exception as e:
            messages.error(request, f"AI parsing failed: {e}")

    return render(request, 'ai_engine/resume_parser.html', {'parsed_data': parsed_data})

@login_required
@require_POST
def generate_job_description(request):
    if not has_ai_access(request.user):
        return JsonResponse({'error': 'AI access is not available for your plan.'}, status=403)

    title = request.POST.get('title', '').strip()
    role = request.POST.get('role', '').strip()
    industry = request.POST.get('industry', '').strip()

    if not title:
        return JsonResponse({'error': 'Job title required.'}, status=400)

    if not jd_pipe:
        return JsonResponse({'error': 'Job description model not available.'}, status=500)

    prompt = (
        f"Write a clear, professional job description for the position titled '{title}'. "
        f"Role: {role or title}. Industry: {industry or 'General'}. "
        "Include responsibilities, qualifications, and benefits in concise paragraphs."
    )

    try:
        out = jd_pipe(prompt, max_length=300, do_sample=False)
        description = out[0].get('generated_text', '').strip()
        # consume token
        consume_user_token(request.user)
        return JsonResponse({'description': description})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
