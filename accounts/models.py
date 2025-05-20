# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    USER_TYPES = [
        ('jobseeker', 'Job Seeker'),
        ('employer', 'Employer'),
        ('superadmin', 'Super Admin'),
    ]
    has_ai_access = models.BooleanField(default=False) 
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='jobseeker')
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'

    def __str__(self):
        return f"{self.username} ({self.user_type})"

class Employer(models.Model):
    EMPLOYER_TYPE_CHOICES = [
        ('direct', 'Direct Hire'),
        ('agency_local', 'Local Agency'),
        ('agency_overseas', 'Overseas Agency'),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employer_profile')
    employer_type = models.CharField(max_length=20, choices=EMPLOYER_TYPE_CHOICES)
    company_name = models.CharField(max_length=255)
    bir_2303 = models.FileField(upload_to='documents/', blank=True, null=True)
    tin = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    official_address = models.TextField(blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company_name} ({self.get_employer_type_display()})"
