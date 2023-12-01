from django.contrib import admin
from django.contrib.auth import get_user_model

from recipes.models import Recipe
from users.models import Follow, FoodgramUser

User = get_user_model()


class BaseFoodrgramUserAdmin(admin.ModelAdmin):
    """Базовая админ-модель с пагинацией."""

    list_per_page = 50
    list_max_show_all = 100


@admin.register(User)
class FoodgramUserAdmin(BaseFoodrgramUserAdmin):
    """
    Преставление, создание, редактирование и удаление пользователей.
    Поля is_admin, followers_count, recipes_count получены с помощью
    дополнительных методов.
    """
    fields = (('username', 'email'), ('first_name', 'last_name'),
              'password', 'role',
              ('is_superuser', 'is_staff'),
              'is_active', 'date_joined')
    list_display = ('id', 'username', 'email', 'followers_count',
                    'recipes_count', 'role', 'is_admin', 'is_staff',
                    'is_superuser')
    list_display_links = ('username', 'id')
    date_hierarchy = 'date_joined'
    search_fields = ('username', 'email', 'id')
    list_per_page = 50
    list_max_show_all = 100
    readonly_fields = ('date_joined',)

    @admin.display(description='Статус администратора',
                   boolean=True)
    def is_admin(self, user: FoodgramUser):
        """Булево значение является ли пользователь администратором."""
        return user.role == 'admin'

    @admin.display(description='Подписчиков')
    def followers_count(self, user: FoodgramUser):
        """Счетчик подписчиков пользователя."""
        return user.following.count()

    @admin.display(description='Рецептов')
    def recipes_count(self, user: FoodgramUser):
        """Счетчик рецептов пользователя."""
        return Recipe.objects.filter(author=user).count()

    def save_model(self, request, obj: FoodgramUser, form, change):
        """
        Создание пользователя.
        Метод переопределен для хеширования пароля и
        автоматической установки статуса персонала,
        если роль пользователя - администратор.
        """
        if obj.role == 'admin':
            obj.is_staff = True
        obj.set_password(obj.password)
        obj.save()


@admin.register(Follow)
class FollowAdmin(BaseFoodrgramUserAdmin):
    """Преставление, создание, редактирование и удаление подписок."""
    fields = (('user', 'following'),)
    list_display = ('id', '__str__', 'user', 'following',
                    'added_date')
    list_display_links = ('__str__', 'id')
    list_filter = ('user__username',)
    search_fields = ('user__username',)
    date_hierarchy = 'added_date'
