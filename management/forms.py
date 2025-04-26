from django import forms
from django.contrib.auth.models import User
from .models import Employer
from django.core.exceptions import ValidationError

class EmployerRegistrationForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()

    class Meta:
        model = Employer
        fields = ['company_name', 'employer_type', 'company_website']

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
