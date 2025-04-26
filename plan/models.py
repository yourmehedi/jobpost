from django.db import models

class Plan(models.Model):
    name = models.CharField(max_length=100)
    job_post_limit = models.IntegerField(default=1)
    resume_access_limit = models.IntegerField(default=0)

    def __str__(self):
        return self.name
