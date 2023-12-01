from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Follow

User = get_user_model()


class BaseFoodrgramUserAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_max_show_all = 100


@admin.register(User)
class FoodgramUserAdmin(BaseFoodrgramUserAdmin):
    fields = (('username', 'email'), ('first_name', 'last_name'),
              'password', 'role',
              ('is_superuser', 'is_staff'),
              'is_active', 'date_joined')
    list_display = ('id', 'username', 'email',
                    'role', 'is_admin', 'is_staff',
                    'is_superuser')
    list_display_links = ('username', 'id')
    date_hierarchy = 'date_joined'
    search_fields = ('username', 'email', 'id')
    list_per_page = 50
    list_max_show_all = 100
    readonly_fields = ('date_joined',)

    def is_admin(self, user):
        return user.role == 'admin'

    def save_model(self, request, obj, form, change):
        obj.set_password(obj.password)
        obj.save()

    is_admin.short_description = 'Статус администратора'
    is_admin.boolean = True


@admin.register(Follow)
class FollowAdmin(BaseFoodrgramUserAdmin):
    fields = (('user', 'following'),)
    list_display = ('id', '__str__', 'user', 'following',
                    'added_date')
    list_display_links = ('__str__', 'id')
    list_filter = ('user__username',)
    search_fields = ('user__username',)
    date_hierarchy = 'added_date'
