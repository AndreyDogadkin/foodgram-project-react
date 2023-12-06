from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram_backend.constants import FoodgramUserConstants


class FoodgramUser(AbstractUser):
    """
    Модель пользователя.
    Поле email переопределено для установки уникальности электронных
    почт пользователей.
    Дополнительное поле role - Выбор пользователь или администратор.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'admin'
        USER = 'user', 'user'

    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта'
    )
    role = models.CharField(
        choices=Role.choices,
        default=Role.USER,
        max_length=FoodgramUserConstants.MAX_LEN_ROLE,
        verbose_name='Роль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return self.username


class Follow(models.Model):
    """
    Модель подписок.
    Связи:
        - user -- Foreign Key c моделью FoodgramUser.
        - following -- Foreign Key c моделью FoodgramUser.
    Ограничения:
        - Нельзя подписаться на одного пользователя несколько раз.
    """

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

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='user_followed_uniq'
            ),
            models.CheckConstraint(
                check=~models.Q(following=models.F('user')),
                name='user_is_not_following'
            ),
        )
        ordering = ('-added_date', )

    def __str__(self):
        return f'{self.user.username} -> {self.following.username}'
