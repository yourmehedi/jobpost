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

    @property
    def is_employer(self):
        return self.user_type == 'employer'

    @property
    def is_jobseeker(self):
        return self.user_type == 'jobseeker'

    @property
    def is_superadmin(self):
        return self.user_type == 'superadmin'


    def __str__(self):
        return f"{self.username} ({self.user_type})"

