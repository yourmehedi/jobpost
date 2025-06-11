from django import forms
from django.contrib.auth import get_user_model
from .models import EmployerProfile
from django.core.exceptions import ValidationError

User = get_user_model()

class EmployerRegistrationForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()

    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'employer_type', 'company_website', 'license_file']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email']
        )
        employer = super().save(commit=False)
        employer.user = user
        if commit:
            employer.save()
        return employer