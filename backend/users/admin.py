from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from recipes.models import Recipe
from users.models import Follow, FoodgramUser

User = get_user_model()


class BaseFoodrgramUserAdmin(UserAdmin):
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
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name',
                                                'last_name',
                                                'email')}),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'role'),
        }),
    )
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
        Метод переопределен для автоматической
        установки статуса персонала,
        если роль пользователя - администратор.
        """
        if obj.role == 'admin':
            obj.is_staff = True
        super().save_model(request, obj, form, change)


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
