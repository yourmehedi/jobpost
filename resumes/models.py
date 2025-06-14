# models.py
import uuid
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # AI Parsed Fields
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)  # Auto-generated tags (comma-separated)
    
    ref_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Tracking ID

    @property
    def file_size(self):
        if self.file and hasattr(self.file, 'size'):
            return self.file.size
        return 0

    def __str__(self):
        return f"{self.user.username} - {self.ref_id}"
