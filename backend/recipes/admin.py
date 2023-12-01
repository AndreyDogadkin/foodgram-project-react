from django.contrib import admin

from .models import (Recipe,
                     Tag,
                     Ingredient,
                     RecipeIngredient,
                     ShoppingList,
                     Favorites)


admin.site.empty_value_display = 'Не задано'


class BaseFoodrgramRecipeAdmin(admin.ModelAdmin):
    """Базовая админ-модель с пагинацией."""

    list_per_page = 50
    list_max_show_all = 100


class InlineIngredients(admin.StackedInline):
    """Инлайн поле для создания и редактирования рецептов."""

    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeFoodrgramRecipeAdmin(BaseFoodrgramRecipeAdmin):
    """
    Представление, создание, редактирование и удаление рецептов.
    Поля ingredients_in_recipe и favorite_count получены
    с помощью дополнительных методов.
    """

    fields = (('name', 'author'),
              'text',
              'tags',
              ('image', 'cooking_time'))
    list_display = ('id', 'name', 'author', 'ingredients_in_recipe',
                    'favorite_count', 'pub_date')
    list_filter = ('author', 'tags')
    list_display_links = ('name', 'id')
    date_hierarchy = 'pub_date'
    inlines = (InlineIngredients, )
    filter_horizontal = ('tags',)
    search_fields = ('name', 'id', 'author__username')

    @admin.display(description='Добавлений в избранное')
    def favorite_count(self, recipe: Recipe):
        """Счетчик добавлений рецепта в избранное."""
        return recipe.favorites.count()

    @admin.display(description='Ингредиенты')
    def ingredients_in_recipe(self, recipe: Recipe):
        """Список ингредиентов рецепта."""
        return list(recipe.ingredients.only('name'))


@admin.register(Tag)
class TagFoodrgramRecipeAdmin(BaseFoodrgramRecipeAdmin):
    """Представление, создание, редактирование и удаление тегов."""

    fields = (('name', 'slug'), 'color')
    list_display = ('id', 'name', 'slug', 'color')
    list_display_links = ('name', 'id')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientFoodrgramRecipeAdmin(BaseFoodrgramRecipeAdmin):
    """Представление, создание, редактирование и удаление ингредиентов."""

    fields = (('name', 'measurement_unit'),)
    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('name', 'id')
    search_fields = ('name', 'id')


@admin.register(ShoppingList)
class ShoppingListFoodrgramRecipeAdmin(BaseFoodrgramRecipeAdmin):
    """
    Представление, создание, редактирование и удаление из списка покупок.
    """

    fields = (('recipe', 'user'), )
    list_display = ('id', '__str__', 'user', 'recipe', 'added_date')
    list_display_links = ('__str__', 'id')
    search_fields = ('recipe__name', 'user__username')


@admin.register(Favorites)
class FavoriteAdmin(ShoppingListFoodrgramRecipeAdmin):
    """
    Представление, создание, редактирование и удаление из избранного.
    """

    pass
