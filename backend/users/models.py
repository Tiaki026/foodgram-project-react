from .validators import (
    validate_email, validate_name,
    validate_nickname, validate_password
)
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Модель кастомного пользователя."""

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validate_nickname],
        verbose_name='Пользователь',
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        validators=[validate_email],
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        validators=[validate_name],
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        validators=[validate_name],
        verbose_name='Фамилия',
    )
    password = models.CharField(
        max_length=150,
        validators=[validate_password],
        verbose_name='Пароль',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='usrname_email_constraint'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'
