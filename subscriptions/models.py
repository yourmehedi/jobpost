
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

User = get_user_model()

class Plan(models.Model):
    DURATION_CHOICES = [
        ('week', 'Weekly'),
        ('month', 'Monthly'),
        ('year', 'Yearly'),
    ]

    name = models.CharField(max_length=100)
    job_limit = models.IntegerField()
    resume_view_limit = models.IntegerField()
    has_ai_access = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES, default='month') 

    def __str__(self):
        return f"{self.name} ({self.get_duration_display()})"

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    ai_tokens = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} - {self.plan}"

    def consume_token(self, count=1):
        if self.ai_tokens >= count:
            self.ai_tokens -= count
            self.save()
            return True
        return False

    def has_tokens(self):
        return self.ai_tokens > 0


@receiver(post_save, sender=Subscription)
def update_user_ai_access(sender, instance, created, **kwargs):
    user = instance.user  
    if instance.active:
        user.has_ai_access = instance.plan.has_ai_access

        if created:
            if instance.plan.has_ai_access:
                token_allocation = {
                    'Free': 5,
                    'Standard': 25,
                    'Premium': 100,
                    'Enterprise': 500,
                }
                instance.ai_tokens = token_allocation.get(instance.plan.name, 10)
                instance.save()
    else:
        user.has_ai_access = False
    user.save()

