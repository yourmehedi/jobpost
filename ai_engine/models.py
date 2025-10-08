from django.db import models
from django.contrib.postgres.fields import JSONField 

class AISettings(models.Model):
    """
    Single-row config for AI integration (admin editable).
    """
    use_openai = models.BooleanField(default=False)
    openai_api_key = models.CharField(max_length=255, blank=True)
    telegram_bot_token = models.CharField(max_length=255, blank=True)
    active_models = models.JSONField(default=dict, blank=True)  # e.g. {"parser":"dslim/bert-base-NER", "matcher":"sentence-transformers/all-MiniLM-L6-v2", ...}
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "AI Settings"

    class Meta:
        verbose_name = "AI Setting"
        verbose_name_plural = "AI Settings"