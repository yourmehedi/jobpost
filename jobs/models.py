from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from accounts.models import CustomUser
from management.models import Employer
from django.utils import timezone
from employers.models import EmployerProfile

class Company(models.Model):
    name = models.CharField(max_length=50, unique=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Job(models.Model):
    title = models.CharField(max_length=70)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    description = models.TextField()
    location = models.CharField(max_length=256)
    formatted_address = models.CharField(max_length=256, blank=True, null=True)
    salary = models.CharField(max_length=50, blank=True, null=True)
    is_email_protected = models.BooleanField(default=True)

    STATUS_CHOICES = [
    ('active', 'Active'),
    ('closed', 'Closed'),
    ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')



    employer = models.ForeignKey('employers.EmployerProfile', on_delete=models.CASCADE, null=True, blank=True)
    skills = models.CharField(max_length=255, blank=True)
    perks = models.CharField(max_length=255, blank=True)
    tech_stack = models.CharField(max_length=255, blank=True)
    vacancies = models.PositiveIntegerField(default=1)
    expiry_date = models.DateField(blank=True, null=True)
    valid_passport = models.BooleanField(default=False)
    principal = models.CharField(max_length=100, blank=True)
    job_role = models.CharField(max_length=100, blank=True)
    experience_level = models.CharField(max_length=100, blank=True)
    job_type = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)

    street = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="Philippines")

    english_required = models.BooleanField(default=False)

    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class JobPost(models.Model):
    employer = models.ForeignKey('employers.EmployerProfile', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, default='default_location')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class JobApplication(models.Model):
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='applications')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField(blank=True)
    reply = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} applied for {self.job.title}"
    

@property
def skill_list(self):
    return self.skills.split(',') if self.skills else []

@property
def perk_list(self):
    return self.perks.split(',') if self.perks else []