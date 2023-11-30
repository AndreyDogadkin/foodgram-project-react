from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminOrHigherOrReadOnly
from api.serializers import (RecipeReadSerializer,
                             RecipeCreateSerializer,
                             TagSerializer,
                             IngredientSerializer,
                             FavoritesSerializer,
                             ShoppingListSerializer)
from api.filters import IngredientNameSearchFilter, CustomRecipeFilter
from api.services import ShoppingListCreator
from recipes.models import (Recipe,
                            Tag,
                            Ingredient,
                            Favorites,
                            ShoppingList)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ...
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ...
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientNameSearchFilter, ]
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """
    ...
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

    def __post_extra_action(self, request: Request, model, pk):
        """
        ...
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
    def __delete_extra_action(request: Request, model, pk):
        """
        ...
        """
        if Recipe.objects.filter(id=pk).exists():
            user = request.user
            recipe: Recipe = Recipe.objects.get(id=pk)
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
        return Response(
            {'errors': 'Выбранный рецепт не существует.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request: Request, pk: int):
        return self.__post_extra_action(
            request=request,
            model=Favorites,
            pk=pk
        )

    @favorite.mapping.delete
    def delete_favorite(self, request: Request, pk: int):
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
        return self.__post_extra_action(
            request=request,
            model=ShoppingList,
            pk=pk
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request: Request, pk: int):
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
        ...
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
