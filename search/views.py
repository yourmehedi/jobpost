from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from resumes.models import Resume
from subscriptions.models import Subscription
from django.contrib import messages

def has_valid_ai_token(user):
    sub = Subscription.objects.filter(employer=user, active=True).first()
    return sub and sub.ai_tokens > 0

@login_required
def tag_search(request):
    if not has_valid_ai_token(request.user):
        messages.error(request, "You need AI access to use resume search.")
        return render(request, 'search/no_access.html')

    query = request.GET.get('q', '').lower()
    tags = [t.strip() for t in query.split(',') if t.strip()]
    
    resumes = Resume.objects.all()
    if tags:
        resumes = resumes.filter(tags__icontains=tags[0])
        for tag in tags[1:]:
            resumes = resumes.filter(tags__icontains=tag)

    return render(request, 'search/search_results.html', {
        'resumes': resumes,
        'query': query
    })
