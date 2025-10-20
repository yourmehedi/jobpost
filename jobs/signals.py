# jobs/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import JobApplication

@receiver(post_save, sender=JobApplication)
def notify_employer_on_application(sender, instance, created, **kwargs):
    if created:
        job = instance.job
        employer = job.employer
        jobseeker = instance.jobseeker

        if employer.email:
            subject = f"New Application for your job: {job.title}"
            message = (
                f"Hello {employer.username},\n\n"
                f"You have received a new job application for your job post '{job.title}'.\n\n"
                f"Applicant: {jobseeker.username}\n"
                f"Email: {jobseeker.email}\n\n"
                f"Please login to your dashboard to review the application.\n\n"
                f"Regards,\nYour Job Portal Team"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [employer.email])
