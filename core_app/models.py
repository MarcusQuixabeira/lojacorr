from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from .validators import validate_cpf


class InsuredManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The e-mail is required")
        email = self.normalize_email(email)
        insured = self.model(email=email, **extra_fields)
        insured.set_password(password)
        insured.save(using=self._db)
        return insured


class Insured(AbstractBaseUser):
    """
    It represents a Insured in the system.
    """
    name = models.CharField(max_length=50, null=False, blank=False)
    cpf = models.CharField(max_length=11, null=False, blank=False, validators=[validate_cpf])
    email = models.EmailField(null=False, blank=False, unique=True)
    created_at = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'name', 'cpf']

    objects = InsuredManager()

    def __str__(self):
        return self.name