from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser
from employers.models import EmployerProfile

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
    EMPLOYER_TYPE_CHOICES = EmployerProfile.EMPLOYER_TYPE_CHOICES

    company_name = forms.CharField(max_length=255)
    employer_type = forms.ChoiceField(choices=EMPLOYER_TYPE_CHOICES)
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
    
class CustomLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_approved:
            raise ValidationError("Your account is pending approval by the admin.", code='inactive')


class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'user_type', 'has_ai_access', 'is_verified',
            'is_approved', 'telegram_chat_id', 'telegram_enabled', 'is_staff', 'is_superuser'
        ]
