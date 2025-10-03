from django.db import models

class FeatureToggle(models.Model):
    key = models.CharField(max_length=100, unique=True)   
    name = models.CharField(max_length=200)               
    enabled = models.BooleanField(default=True)          

    def __str__(self):
        return f"{self.name} ({'ON' if self.enabled else 'OFF'})"
