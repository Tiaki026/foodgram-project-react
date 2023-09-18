import re

from django.core.exceptions import ValidationError


def validate_name(value):
    """Проверка написания только одним языком."""
    regex = r'^[a-zA-Zа-яёА-ЯЁ\s-]+$'
    if not re.match(regex, value):
        raise ValidationError('Используйте только кириллицу или латиницу.')


def validate_email(value):
    """Проверка формата email."""
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-]{1,10}$'
    if not re.match(regex, value):
        raise ValidationError('Неверный формат электронной почты.')


def validate_nickname(value):
    """Проверка формата никнейма."""
    regex = r'^[a-zA-Z0-9_.-]{2,}$'
    if not re.match(regex, value):
        raise ValidationError(
            'Никнейм содержит недопустимые символы или менее 2 символов.'
        )


def validate_password(value):
    """Проверка требований пароля."""
    regex = (
        r'^(?=.*[A-Z])(?=.*[0-9!@#$%^&*()_+=-])[a-zA-Z0-9!@#$%^&*()_+=-]{8,}$'
    )
    if not re.match(regex, value):
        raise ValidationError(
            'Пароль должен состоять из латинских символов, '
            'иметь как минимум одну заглавную букву, '
            'одну цифру или специальный символ '
            'и быть не менее 8 символов.'
        )
