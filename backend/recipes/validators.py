import re

from django.core.exceptions import ValidationError


def validate_tag(value):
    """Проверка формата тега."""
    regex = r'^[-a-zA-Z0-9_]+$'
    if not re.match(regex, value):
        raise ValidationError(
            'Используйте только латиницу, цифры и "_".'
        )


def validate_hex_color(value):
    """Проверка формата HEX-цвета."""
    if not value.startswith('#'):
        raise ValidationError('Код цвета должен начинаться с #')

    hex_digits = value[1:]
    valid_hex_characters = set('0123456789ABCDEFabcdef')
    if any(char not in valid_hex_characters for char in hex_digits):
        raise ValidationError('Неверный формат цвета')

    if len(hex_digits) < 6:
        raise ValidationError('Неверная длина цвета')
