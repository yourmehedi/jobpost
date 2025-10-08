from django import forms
from .models import AISettings
import json

class AISettingsForm(forms.ModelForm):
    class Meta:
        model = AISettings
        fields = ("use_openai", "openai_api_key", "telegram_bot_token", "active_models")

    def clean_active_models(self):
        data = self.cleaned_data.get("active_models")
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                raise forms.ValidationError("active_models must be valid JSON.")
        return data
