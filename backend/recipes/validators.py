import webcolors
from django.core.exceptions import ValidationError


def validate_hex_color(value):
    """Валидатор hex."""
    try:
        webcolors.normalize_hex(value)
    except ValueError:
        raise ValidationError(f'"{value}" не является hex цветом.')
