from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientNameSearchFilter, CustomRecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminOrHigherOrReadOnly
from api.serializers import (RecipeReadSerializer,
                             RecipeCreateSerializer,
                             TagSerializer,
                             IngredientSerializer,
                             FavoritesSerializer,
                             ShoppingListSerializer)
from api.services import ShoppingListCreator
from recipes.models import (Recipe,
                            Tag,
                            Ingredient,
                            Favorites,
                            ShoppingList)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для представления ингредиентов.
    Методы:
        - GET -- Представление списка тегов.
        - GET -- Представление тега по id.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для представления ингредиентов.
    Методы:
        - GET -- Представление списка ингредиентов.
        - GET -- Представление ингредиента по id.
    Доступен поиск по частичному вхождению в название ингредиента.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientNameSearchFilter, ]
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """
    Вьюсет для представления, создания, редактирования и удаления рецептов.
    Права доступа:
        - Просмотр объектов доступен всем пользователям
        - Создание объектов доступно только авторизованным пользователям
        - Редактирование объектов доступно только авторам или пользователям
        со статусом персонала.
    Доступные методы:
        - GET -- Представление списка рецептов.
        - GET -- Представление рецепта по id.
        - POST -- Создание рецепта.
        - PATCH -- Редактирование рецепта.
        - DELETE -- Удаление рецепта.
    Доступные actions:
        - POST -- Добавление рецепта в избранное.
        - DELETE -- Удаление рецепта из избранного.
        - POST -- Добавление рецепта в список покупок.
        - DELETE -- Удаление рецепта из списка покупок.
        - GET -- Получить список покупок в формате .txt.
    Параметры фильтрации:
        - is_favorited=<0 или 1> -- 1 Только рецепты добавленные в избранное
        - is_in_shopping_cart=<0 или 1> -- Только рецепты в списке покупок
        - author=<id> -- Только рецепты выбранного автора
        - tags=<slug> -- Только рецепты с выбранными тегами
            Пример: tags=lunch&tags=breakfast
        Пагинация:
        - page=<int> - Номер страницы
        - limit=<int> - Количество объектов на странице(по умолчанию 6)
    """

    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrAdminOrHigherOrReadOnly,
                          IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = CustomRecipeFilter
    pagination_class = CustomPagination

    def update(self, request: Request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                            data={'detail': 'Метод "PUT" не разрешен.'})
        return super().update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        elif self.action == 'favorite':
            return FavoritesSerializer
        elif self.action == 'shopping_cart':
            return ShoppingListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer: RecipeCreateSerializer):
        user = self.request.user
        serializer.is_valid(raise_exception=True)
        serializer.save(author=user)

    def __post_extra_action(self, request: Request, model, pk: int):
        """
        Добавление рецепта в список покупок/избранное.
        Ограничения:
            - Невозможно добавить рецепт, который не существует.
            - Невозможно добавить уже добавленный рецепт.
        """
        if Recipe.objects.filter(id=pk).exists():
            user = request.user
            recipe: Recipe = Recipe.objects.get(id=pk)
            object_exists: bool = model.objects.filter(
                user=user,
                recipe=recipe
            ).exists()
            if object_exists:
                return Response(
                    {'errors': 'Выбранный рецепт уже добавлен.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, recipe=recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED)
        return Response(
            {'errors': 'Выбранный рецепт не существует.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def __delete_extra_action(request: Request, model, pk: int):
        """
        Удаление рецепта из списка покупок/избранного.
        Ограничения:
            - Невозможно удалить рецепт, который не существует.
            - Невозможно удалить рецепт, который не добавлен.
        """
        user = request.user
        recipe: Recipe = get_object_or_404(Recipe, id=pk)
        object_exists: bool = model.objects.filter(
            user=user,
            recipe=recipe
        ).exists()
        if not object_exists:
            return Response(
                data={'errors': 'Выбранный рецепт ранее не был добавлен.'},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request: Request, pk: int):
        """
        Добавить рецепт в избранное.
        Доступно только авторизованным пользователям.
        """
        return self.__post_extra_action(
            request=request,
            model=Favorites,
            pk=pk
        )

    @favorite.mapping.delete
    def delete_favorite(self, request: Request, pk: int):
        """
        Удалить рецепт из избранного.
        Доступно только авторизованным пользователям.
        """
        return self.__delete_extra_action(
            request=request,
            model=Favorites,
            pk=pk
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request: Request, pk: int):
        """
        Добавить рецепт в список покупок.
        Доступно только авторизованным пользователям.
        """
        return self.__post_extra_action(
            request=request,
            model=ShoppingList,
            pk=pk
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request: Request, pk: int):
        """
        Удалить рецепт из списка покупок.
        Доступно только авторизованным пользователям.
        """
        return self.__delete_extra_action(
            request=request,
            model=ShoppingList,
            pk=pk
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request: Request):
        """
        Получить список покупок в формате .txt.
        Доступно только авторизованным пользователям.
        При создании списка повторяющиеся ингредиенты складываются.
        Пример:
            - Рецепт 1:
                - Персики 3 шт.
            - Рецепт 2:
                - Персики 2 шт.
            Список покупок:
                - Персики - 5 шт.
        """
        user = request.user
        if user.shop_list.exists():
            shopping_list = ShoppingListCreator(
                user=user
            ).create_shopping_list()
            response = HttpResponse(shopping_list, content_type='text/plain')
            response['Content-Disposition'] = (
                f'attachment; filename={user.username}_shopping_list.txt'
            )
            return response

        return Response(
            data={'errors': 'Список покупок пуст.'},
            status=status.HTTP_400_BAD_REQUEST
        )
