# employer/models.py
from django.db import models
from django.contrib.auth.models import User
from subscriptions.models import Plan

# class EmployerProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)

#     def job_post_count(self):
#         return self.job_set.count()

#     def can_post_job(self):
#         if not self.plan:
#             return False
#         return self.job_post_count() < self.plan.job_post_limit

# class Job(models.Model):
#     employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title

# def post_job(request):
#     if not request.user.is_authenticated:
#         return redirect('login')

#     try:
#         employer_profile = EmployerProfile.objects.get(user=request.user)
#     except EmployerProfile.DoesNotExist:
#         # Redirect to a profile creation page or show error
#         return redirect('create_employer_profile')  # Or show a message

#     if not employer_profile.can_post_job():
#         return render(request, 'employers/limit_reached.html')