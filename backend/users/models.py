from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodgramUser(AbstractUser):

    ROLE_CHOICES = (
        ('user', 'user'),
        ('admin', 'admin'),
    )

    role = models.CharField(
        choices=ROLE_CHOICES,
        default='user',
        max_length=8
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def is_admin(self):
        return self.role == 'admin'

    def __str__(self):
        return self.username
