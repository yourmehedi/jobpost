from django import forms
from .models import EmployerProfile

class EmployerRegistrationForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'employer_type', 'license_number', 'license_file']

    def clean(self):
        cleaned_data = super().clean()
        employer_type = cleaned_data.get('employer_type')
        license_file = cleaned_data.get('license_file')
        license_number = cleaned_data.get('license_number')

        if employer_type in ['local_agency', 'overseas_agency']:
            if not license_file:
                self.add_error('license_file', 'License file is required for selected employer type.')
            if not license_number:
                self.add_error('license_number', 'License number is required for selected employer type.')
