from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'description', 'location',
            'salary', 'status', 'skills', 'perks',
            'tech_stack', 'vacancies', 'expiry_date',
            'valid_passport', 'principal', 'job_role',
            'experience_level', 'job_type', 'industry',
            'street', 'city', 'province', 'zip_code', 'country',
            'english_required'
        ]
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }
