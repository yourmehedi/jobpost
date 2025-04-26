# employer/views.py
from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# @login_required
# def post_job(request):
#     profile = EmployerProfile.objects.get(user=request.user)

#     if not profile.can_post_job():
#         return render(request, 'employer/job_limit_exceeded.html')

#     if request.method == 'POST':
#         title = request.POST.get('title')
#         description = request.POST.get('description')
#         Job.objects.create(employer=profile, title=title, description=description)
#         return redirect('job_success')

#     return render(request, 'employer/post_job.html')

# def job_success(request):
#     return render(request, 'employer/job_success.html')

# def dashboard(request):
#     return HttpResponse('slsns')