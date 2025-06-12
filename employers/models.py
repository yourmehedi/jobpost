from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import *

User = get_user_model()

class EmployerProfile(models.Model):
    EMPLOYER_TYPE_CHOICES = [
        ('company', 'Company'),
        ('individual', 'Individual'),
        ('agency', 'Agency'),
        ('ngo', 'NGO'),
        ('government', 'Government'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=255)
    employer_type = models.CharField(max_length=50, choices=EMPLOYER_TYPE_CHOICES)  
    company_website = models.URLField(blank=True, null=True)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    license_file = models.FileField(upload_to='licenses/', blank=True, null=True)
    license_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    official_address = models.TextField(blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    tin = models.CharField(max_length=100, blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

