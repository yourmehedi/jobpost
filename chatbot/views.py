# # chatbot/views.py
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.http import require_POST
# from transformers import pipeline
# from subscriptions.models import Subscription

# # ✅ Helper to check if user has AI access
# def has_valid_ai_token(user):
#     sub = Subscription.objects.filter(employer=user, active=True).first()
#     return sub and sub.ai_tokens > 0


# # ✅ Load Hugging Face model globally once
# try:
#     chatbot_model = pipeline("text-generation", model="microsoft/DialoGPT-medium")
# except Exception as e:
#     print("⚠️ Failed to load chatbot model:", e)
#     chatbot_model = None


# @csrf_exempt
# @login_required
# @require_POST
# def chatbot_reply(request):
#     """
#     Hugging Face Chatbot (Offline fallback to OpenAI-like behavior)
#     """
#     if not has_valid_ai_token(request.user):
#         return JsonResponse({'error': 'No AI tokens left.'}, status=403)

#     user_question = request.POST.get('question', '').strip()
#     if not user_question:
#         return JsonResponse({'error': 'No question received.'}, status=400)

#     try:
#         if not chatbot_model:
#             return JsonResponse({'error': 'Chatbot model not available.'}, status=500)

#         # ✅ Prepend site context (like OpenAI prompt)
#         context = (
#             "You are a helpful assistant for a job recruitment platform. "
#             "Assist users with posting jobs, applying, using AI resume tools, or managing subscriptions. "
#             "Answer in a friendly and human-like tone.\n\nUser: "
#         )
#         input_text = context + user_question

#         response = chatbot_model(input_text, max_length=150, num_return_sequences=1)
#         answer = response[0]['generated_text'].replace(input_text, '').strip()

#         # Optional — Deduct AI token usage
#         sub = Subscription.objects.filter(employer=request.user, active=True).first()
#         if sub:
#             sub.consume_token()

#         return JsonResponse({'answer': answer})

#     except Exception as e:
#         print("Chatbot Error:", e)
#         return JsonResponse({'error': str(e)}, status=500)


# chatbot/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from transformers import pipeline
from subscriptions.models import Subscription

# Load a lightweight conversational model (or distilgpt2 for CPU)
try:
    chat_pipe = pipeline("text-generation", model="microsoft/DialoGPT-medium")
except Exception as e:
    print("⚠️ chatbot model load error:", e)
    chat_pipe = None

def has_valid_ai_token(user):
    sub = Subscription.objects.filter(employer=user, active=True).first()
    return sub and sub.ai_tokens > 0

@csrf_exempt
@login_required
@require_POST
def chatbot_reply(request):
    if not has_valid_ai_token(request.user):
        return JsonResponse({'error': 'No AI tokens left.'}, status=403)

    user_question = request.POST.get('question', '').strip()
    if not user_question:
        return JsonResponse({'error': 'No question sent.'}, status=400)

    if not chat_pipe:
        return JsonResponse({'error': 'Chat model not available on server.'}, status=500)

    try:
        context = (
            "You are a friendly assistant for a job recruitment site. Help users with job posting, applying, subscriptions and profile. "
        )
        prompt = context + "\nUser: " + user_question + "\nAssistant:"
        resp = chat_pipe(prompt, max_length=150, do_sample=False)
        generated = resp[0].get('generated_text', '')
        # minimal cleanup
        answer = generated.replace(prompt, '').strip() if prompt in generated else generated.strip()

        # consume token if needed
        sub = Subscription.objects.filter(employer=request.user, active=True).first()
        if sub:
            sub.consume_token()

        return JsonResponse({'answer': answer})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
