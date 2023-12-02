from art import text2art
from django.db.models import Sum

from recipes.models import RecipeIngredient


class ShoppingListCreator:
    """
    Создание списка покупок.
    Пример:
        Список покупок для @<username>.

        ◻︎ бараний окорок на косточке --------- 10 кусок
        ◻︎ масло грецкого ореха --------------- 50 ч. л.
        ◻︎ персики консервированные ----------- 10 г
        """

    def __init__(self, user):
        self.user = user

    def __get_data(self):
        """
        Получение ингредиентов и суммирование количества дублей.
        """
        shopping_list_data = RecipeIngredient.objects.filter(
            recipe__shop_list__user=self.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            sum_amount=Sum(
                'amount',
                distinct=True
            )
        )
        return shopping_list_data

    def create_shopping_list(self):
        """
        Создание списка покупок.
        """
        data = self.__get_data()
        separator = '-'
        base_len_separator = 35
        shop_list = text2art('Foodgram\n\n', font='small')
        shop_list += f'Список покупок для @{self.user.username}.\n\n'
        for item in data:
            item_len_separator = (
                base_len_separator - len(item["ingredient__name"])
            )
            shop_list += (
                f'◻︎ {item["ingredient__name"]} '
                f'{separator * item_len_separator} '
                f'{item["sum_amount"]} '
                f'{item["ingredient__measurement_unit"]}\n'
            )
        return shop_list
