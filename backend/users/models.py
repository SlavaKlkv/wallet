from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from core.constants import EMAIL_MAX_LENGTH, NAME_MAX_LENGTH
from core.managers import UserManager


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
        verbose_name="Адрес электронной почты"
    )
    username = models.CharField(
        unique=True,
        max_length=NAME_MAX_LENGTH,
        verbose_name="Имя пользователя",
        validators=[UnicodeUsernameValidator()],
    )
    first_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name="Фамилия"
    )
    avatar = models.ImageField(
        "Аватар",
        upload_to="users/",
        blank=False,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ()
    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
