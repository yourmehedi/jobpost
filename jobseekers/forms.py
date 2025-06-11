from django import forms
from .models import Jobseeker
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm

class JobseekerForm(forms.ModelForm):
    class Meta:
        model = Jobseeker
        fields = [
            'full_name', 'date_of_birth', 'gender', 'contact_number',
            'email', 'preferred_country', 'preferred_city',
            'passport_number', 'national_id', 'address'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class JobseekerSettingsForm(forms.ModelForm):
    class Meta:
        model = Jobseeker
        fields = [
            'full_name', 'date_of_birth', 'gender', 'contact_number',
            'email', 'preferred_country', 'preferred_city',
            'passport_number', 'national_id', 'address'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Jobseeker
        fields = ['document_upload']

# Avoid name clash with Django’s PasswordChangeForm
class PasswordChangeForm(DjangoPasswordChangeForm):
    pass
