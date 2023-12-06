import django_filters
from django import forms
from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class NoValidationMultipleChoiceField(forms.MultipleChoiceField):

    def validate(self, value):
        pass


class CustomTagFilter(django_filters.AllValuesMultipleFilter):
    field_class = NoValidationMultipleChoiceField


class IngredientNameSearchFilter(SearchFilter):
    """Фильтр поиска по имени ингредиента."""
    search_param = 'name'


class CustomRecipeFilter(FilterSet):
    """
    Фильтр поиска рецептов.
    Параметры фильтрации:
    - is_favorited=<0 или 1> -- 1 Только рецепты добавленные в избранное
    - is_in_shopping_cart=<0 или 1> -- Только рецепты в списке покупок
    - author=<id> -- Только рецепты выбранного автора
    - tags=<slug> -- Только рецепты с выбранными тегами
        Пример: tags=lunch&tags=breakfast
    """
    tags = CustomTagFilter(field_name='tags__slug',
                           label='Теги')
    is_favorited = filters.NumberFilter(
        method='filter_is_favorited',
        max_value=1, min_value=0, label='В избранном')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart',
        max_value=1, min_value=0, label='В корзине')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shop_list__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart',
                  'author', 'tags')
