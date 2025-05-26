from django.db import models

class RestrictedWord(models.Model):
    word = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.word
