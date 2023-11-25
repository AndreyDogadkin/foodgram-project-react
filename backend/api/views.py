from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.pagination import RecipePagination
from api.permissions import AdminOrReadOnly
from api.serializers import (RecipeReadSerializer,
                             RecipeCreateSerializer,
                             TagSerializer,
                             IngredientSerializer,
                             FavoritesSerializer)
from recipes.models import Recipe, Tag, Ingredient, User, Favorites


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly, )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):

    queryset = Recipe.objects.all()
    # permission_classes = None  # TODO Добавить права доступа
    # filter_backends = None
    pagination_class = RecipePagination

    def update(self, request: Request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                            data={'detail': 'Метод "PUT" не разрешен.'})
        return super().update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer: RecipeCreateSerializer):
        user = User.objects.first()  # TODO Исправить на /user = self.request.user/
        serializer.save(author=user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        # permission_classes = [],  # TODO Добавить права доступа
    )
    def favorite(self, request: Request, *args, **kwargs):
        recipe_id = kwargs.get('pk')
        user = User.objects.first()  # TODO Исправить на /user = self.request.user/
        recipe: Recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite_exists: bool = Favorites.objects.filter(user=user, recipe=recipe).exists()
        if request.method == 'POST':
            if favorite_exists:
                return Response(
                    {'errors': 'Выбранный рецепт уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FavoritesSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not favorite_exists:
            return Response(data={'errors': 'Выбранный рецепт не находится в избранном.'},
                            status=status.HTTP_400_BAD_REQUEST)

        Favorites.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

