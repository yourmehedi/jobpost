
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

class Plan(models.Model):
    name = models.CharField(max_length=100)
    job_limit = models.IntegerField()
    resume_view_limit = models.IntegerField()
    has_ai_access = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.employer} - {self.plan}"

@receiver(post_save, sender=Subscription)
def update_user_ai_access(sender, instance, **kwargs):
    user = instance.employer
    if instance.active:
        user.has_ai_access = instance.plan.has_ai_access
    else:
        user.has_ai_access = False
    user.save()