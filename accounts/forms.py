# accounts/forms.py
from django import forms
from .models import CustomUser
from employers.models import EmployerProfile
from django.contrib.auth.forms import UserCreationForm

class JobseekerRegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'jobseeker'
        if commit:
            user.save()
        return user


class EmployerFullRegisterForm(UserCreationForm):
    EMPLOYER_TYPE_CHOICES = EmployerProfile.EMPLOYER_TYPE_CHOICES  # 🟢 Reuse from model

    company_name = forms.CharField(max_length=255)
    employer_type = forms.ChoiceField(choices=EMPLOYER_TYPE_CHOICES)  # 👈 ChoiceField here
    company_website = forms.URLField(required=False)
    license_number = forms.CharField(required=False)
    license_file = forms.FileField(required=False)
    official_address = forms.CharField(widget=forms.Textarea, required=False)
    contact_number = forms.CharField(required=False)
    tin = forms.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'employer'
        if commit:
            user.save()
        return user
