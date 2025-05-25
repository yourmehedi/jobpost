# chatbot/views.py

import openai
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from subscriptions.models import Subscription

def has_valid_ai_token(user):
    sub = Subscription.objects.filter(employer=user, active=True).first()
    return sub and sub.ai_tokens > 0

@csrf_exempt
@login_required
@require_POST
def chatbot_reply(request):
    if not has_valid_ai_token(request.user):
        return JsonResponse({'error': 'No AI tokens left.'}, status=403)

    user_question = request.POST.get('question', '')

    if not user_question:
        return JsonResponse({'error': 'No question received.'}, status=400)

    try:
        openai.api_key = settings.OPENAI_API_KEY

        system_prompt = (
            "You are a helpful assistant for a job platform. "
            "Guide users on how to use the website: job posting, applying, subscription, profile setup, etc."
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ]
        )

        answer = response['choices'][0]['message']['content'].strip()

        return JsonResponse({'answer': answer})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
