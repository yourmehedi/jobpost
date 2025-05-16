# ai_engine/views.py

import openai
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def resume_parser(request):
    if not request.user.has_ai_access:
        messages.error(request, "This is a premium feature. Please upgrade your plan.")
        return redirect('subscriptions:plan_list')

    parsed_data = None

    if request.method == 'POST':
        resume_text = request.POST.get('resume_text')
        if resume_text:
            try:
                openai.api_key = settings.OPENAI_API_KEY

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You're a resume parser AI. Extract structured info from text."},
                        {"role": "user", "content": f"Extract key info from this resume:\n\n{resume_text}"}
                    ]
                )

                parsed_data = response['choices'][0]['message']['content']

            except Exception as e:
                messages.error(request, f"Something went wrong: {str(e)}")

        else:
            messages.error(request, "Please enter resume text.")

    return render(request, 'ai_engine/resume_parser.html', {
        'parsed_data': parsed_data
    })
