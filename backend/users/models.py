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

    def is_admin(self):
        return self.role == 'admin'

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        to=FoodgramUser,
        verbose_name='Пользователь',
        related_name='follower',
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        to=FoodgramUser,
        verbose_name='Подписан',
        related_name='following',
        on_delete=models.CASCADE
    )
    added_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки',
        editable=False
    )

    def __str__(self):
        return f'{self.user.username} -> {self.following.username}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='user_followed_uniq'
            ),
        )
