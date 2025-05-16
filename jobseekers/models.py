from accounts.models import CustomUser
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Jobseeker(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    contact_number = models.CharField(max_length=20)
    address = models.TextField()
    job_type_preference = models.CharField(
        max_length=50,
        choices=[('local', 'Local'), ('abroad', 'Abroad'), ('remote', 'Remote')],
        default='local'
    )
    preferred_country = models.CharField(max_length=100, blank=True, null=True)
    preferred_city = models.CharField(max_length=100, blank=True, null=True)
    passport_number = models.CharField(max_length=50, blank=True, null=True)
    national_id = models.CharField(max_length=50, blank=True, null=True)
    document_upload = models.FileField(upload_to='documents/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Education(models.Model):
    jobseeker = models.ForeignKey(Jobseeker, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    currently_studying = models.BooleanField(default=False)

class WorkExperience(models.Model):
    jobseeker = models.ForeignKey(Jobseeker, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    currently_working = models.BooleanField(default=False)
    responsibilities = models.TextField(blank=True)

class Skill(models.Model):
    name = models.CharField(max_length=100)

class JobseekerSkill(models.Model):
    jobseeker = models.ForeignKey(Jobseeker, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.CharField(
        max_length=50,
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('expert', 'Expert')]
    )

class Language(models.Model):
    jobseeker = models.ForeignKey(Jobseeker, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=50)
    proficiency = models.CharField(
        max_length=50,
        choices=[('basic', 'Basic'), ('fluent', 'Fluent'), ('native', 'Native')]
    )

class Reference(models.Model):
    jobseeker = models.ForeignKey(Jobseeker, on_delete=models.CASCADE, related_name='references')
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=100)
    relationship = models.CharField(max_length=100)

class AdditionalInfo(models.Model):
    jobseeker = models.OneToOneField(Jobseeker, on_delete=models.CASCADE, related_name='additional_info')
    about_me = models.TextField(blank=True, null=True)
    achievements = models.TextField(blank=True, null=True)
    hobbies = models.TextField(blank=True, null=True)

@property
def age(self):
    from datetime import date
    if self.date_of_birth:
        return date.today().year - self.date_of_birth.year
    return None
