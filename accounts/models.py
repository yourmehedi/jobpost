from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    is_employer = models.BooleanField(default=False)
    is_agency = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.email


class Employer(models.Model):
    USER_TYPE_CHOICES = [
        ('direct', 'Direct Hire'),
        ('agency_local', 'Local Agency'),
        ('agency_overseas', 'Overseas Agency'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts_employer')
    employer_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.get_employer_type_display()})"
