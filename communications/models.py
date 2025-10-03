from django.conf import settings
from django.db import models

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_messages',
        on_delete=models.CASCADE
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_broadcast = models.BooleanField(default=False)  # Added for broadcast messages

    def __str__(self):
        return f"{self.subject} ({self.sender} → {self.recipient})"


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    ROLE_CHOICES = [
        ('all', 'All Users'),
        ('jobseeker', 'Jobseeker'),
        ('employer', 'Employer'),
        ('superadmin', 'Super Admin'),
    ]
    target_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='all')

    def __str__(self):
        return f"Notification to {self.user} - {self.title}"


class Broadcast(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='broadcasts', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    ROLE_CHOICES = [
        ('all', 'All Users'),
        ('jobseeker', 'Jobseekers'),
        ('employer', 'Employers'),
        ('specific', 'Specific Users'),
    ]
    target_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='all')
    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='manual_broadcasts', blank=True)

    def __str__(self):
        return f"Broadcast ({self.target_role}) by {self.sender}"
