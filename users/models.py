from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    balance = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("аккаунт")
        verbose_name_plural = _("аккаунты")

    def __str__(self):
        return self.username
