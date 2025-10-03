from django.db import models
from django.conf import settings 
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser


EMPLOYER_TYPE_CHOICES = [
    ('direct', 'Direct Hire Employer'),
    ('local_agency', 'Recruitment Agency (Local)'),
    ('overseas_agency', 'Recruitment Agency (Overseas)'),
]

APPROVAL_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

class Employer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='management_employer')
    company_name = models.CharField(max_length=255)
    company_website = models.URLField(blank=True, null=True)
    employer_type = models.CharField(max_length=20, choices=EMPLOYER_TYPE_CHOICES)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    license_file = models.FileField(upload_to='licenses/', blank=True, null=True)  
    address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} ({self.get_employer_type_display()})"


class ContactMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.user.user_type if self.user else 'Guest'})"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)  
def create_employer_profile(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        pass 


