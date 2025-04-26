from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

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
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
class JobPost(models.Model):
    employer = models.ForeignKey('accounts.Employer', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
