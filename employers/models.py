from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

EMPLOYER_TYPES = [
    ('direct', 'Direct Hire (Individual/Company)'),
    ('local_agency', 'Local Recruitment Agency'),
    ('overseas_agency', 'Overseas Recruitment Agency'),
]

class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    employer_type = models.CharField(max_length=20, choices=EMPLOYER_TYPES)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    license_file = models.FileField(upload_to='licenses/', blank=True, null=True)
    license_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name
