from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('user_type', 'superadmin') 

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    USER_TYPES = [
        ('jobseeker', 'Job Seeker'),
        ('employer', 'Employer'),
        ('superadmin', 'Super Admin'),
    ]

    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='jobseeker')
    has_ai_access = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    telegram_chat_id = models.CharField(max_length=100, blank=True, null=True)
    telegram_enabled = models.BooleanField(default=False)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'

    objects = CustomUserManager()

    @property
    def is_employer(self):
        return self.user_type == 'employer'

    @property
    def is_jobseeker(self):
        return self.user_type == 'jobseeker'

    @property
    def is_superadmin(self):
        return self.user_type == 'superadmin'

    def save(self, *args, **kwargs):
        if self.is_superuser and self.user_type != 'superadmin':
            self.user_type = 'superadmin'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.user_type})"
