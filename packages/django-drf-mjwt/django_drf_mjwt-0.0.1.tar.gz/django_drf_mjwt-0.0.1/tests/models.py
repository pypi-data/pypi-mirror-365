import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class EmailUserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class EmailUser(AbstractUser):
    """
    Custom user model that uses email as the username field
    """

    username = None  # Remove username field
    email = models.EmailField(unique=True)
    secret = models.CharField(max_length=256, default=uuid.uuid4)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Remove email from required fields since it's the username

    objects = EmailUserManager()

    class Meta:
        app_label = "tests"
