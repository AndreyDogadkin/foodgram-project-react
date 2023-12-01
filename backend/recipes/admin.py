from django.contrib import admin

from .models import (Recipe,
                     Tag,
                     Ingredient,
                     RecipeIngredient,
                     ShoppingList,
                     Favorites)


admin.site.empty_value_display = 'Не задано'


class BaseFoodrgramRecipeAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_max_show_all = 100


class InlineIngredients(admin.StackedInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeFoodrgramRecipeAdmin(BaseFoodrgramRecipeAdmin):
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
        return recipe.favorites.count()

    @admin.display(description='Ингредиенты')
    def ingredients_in_recipe(self, recipe: Recipe):
        return list(recipe.ingredients.only('name'))


@admin.register(Tag)
class TagFoodrgramRecipeAdmin(BaseFoodrgramRecipeAdmin):
    fields = (('name', 'slug'), 'color')
    list_display = ('id', 'name', 'slug', 'color')
    list_display_links = ('name', 'id')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientFoodrgramRecipeAdmin(BaseFoodrgramRecipeAdmin):
    fields = (('name', 'measurement_unit'),)
    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('name', 'id')
    search_fields = ('name', 'id')


@admin.register(ShoppingList)
class ShoppingListFoodrgramRecipeAdmin(BaseFoodrgramRecipeAdmin):
    fields = (('recipe', 'user'), )
    list_display = ('id', '__str__', 'user', 'recipe', 'added_date')
    list_display_links = ('__str__', 'id')
    search_fields = ('recipe__name', 'user__username')


@admin.register(Favorites)
class FavoriteAdmin(ShoppingListFoodrgramRecipeAdmin):
    pass
