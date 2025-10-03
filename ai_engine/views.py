import openai
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from subscriptions.models import Subscription
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

@login_required
def resume_parser(request):
    # Check AI access based on subscription tokens
    if not Subscription.objects.filter(employer=request.user, active=True, ai_tokens__gt=0).exists():
        messages.error(request, "This is a premium feature. Please upgrade your plan.")
        return redirect('subscriptions:plan_list')

    parsed_data = None

    if request.method == 'POST':
        resume_text = request.POST.get('resume_text', '')
        if resume_text.strip():
            try:
                openai.api_key = settings.OPENAI_API_KEY

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You're a resume parser AI. Extract structured info from text in bullet points (Name, Email, Phone, Skills, Experience, Education)."},
                        {"role": "user", "content": resume_text}
                    ]
                )

                parsed_data = response['choices'][0]['message']['content'].strip()

            except Exception as e:
                messages.error(request, f"Something went wrong: {str(e)}")

        else:
            messages.error(request, "Please enter resume text.")

    return render(request, 'ai_engine/resume_parser.html', {
        'parsed_data': parsed_data
    })


def consume_user_token(user):
    subscription = Subscription.objects.filter(employer=user, active=True).first()
    if subscription and subscription.consume_token():
        return True
    return False


@login_required
@require_POST
def generate_job_description(request):
    # ✅ Fix field name (use user instead of employer)
    if not Subscription.objects.filter(user=request.user, active=True, ai_tokens__gt=0).exists():
        return JsonResponse({'error': 'AI access is not available for your plan.'}, status=403)

    title = request.POST.get('title', '').strip()
    role = request.POST.get('role', '').strip()
    industry = request.POST.get('industry', '').strip()

    if not title:
        return JsonResponse({'error': 'Job title is required.'}, status=400)

    try:
        openai.api_key = settings.OPENAI_API_KEY
        prompt = (
            f"Write a professional and detailed job description for a position titled '{title}' "
            f"in the '{industry or 'general'}' industry. The role of the candidate will be '{role or title}'."
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert job description writer."},
                {"role": "user", "content": prompt}
            ]
        )

        description = response['choices'][0]['message']['content'].strip()

        # ✅ Deduct token (also use user instead of employer)
        subscription = Subscription.objects.filter(user=request.user, active=True).first()
        if subscription:
            subscription.consume_token()

        return JsonResponse({'description': description})

    
    except openai.error.RateLimitError:
        return JsonResponse({'error': 'OpenAI quota exceeded. Please check your API plan or key.'}, status=429)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
