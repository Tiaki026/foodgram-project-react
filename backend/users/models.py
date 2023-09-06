from .validators import (
    validate_email, validate_name,
    validate_nickname, validate_password
)
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


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


class Subscription(models.Model):
    """Модель подписчиков."""

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='subscribing',
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscriber',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки',
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ['-pub_date']
        unique_together = ['author', 'user']

    def __str__(self) -> str:
        return f'{self.user.username} подписан на {self.author.username}.'

    def clean(self):
        """Запрет подписки на самого себя."""
        super().clean()
        if self.subscriber == self.author:
            raise ValidationError('Нельзя подписываться на самого себя.')
        if Subscription.objects.filter(
            subscriber=self.subscriber, author=self.author
        ).exists():
            raise ValidationError('Вы уже подписаны на этого автора.')
