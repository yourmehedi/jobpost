# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from jobseekers.models import Jobseeker

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_jobseeker_profile(sender, instance, created, **kwargs):
    if instance.user_type == "jobseeker":  
        jobseeker, new = Jobseeker.objects.get_or_create(user=instance)
        
        # Auto-fill fields from email / user object
        jobseeker.full_name = instance.get_full_name() or instance.username  
        jobseeker.email = instance.email  

        # default / empty values (optional)
        if not jobseeker.contact_number:
            jobseeker.contact_number = "N/A"
        if not jobseeker.gender:
            jobseeker.gender = "other"
        
        jobseeker.save()
