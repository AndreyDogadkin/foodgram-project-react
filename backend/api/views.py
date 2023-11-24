from rest_framework import viewsets, filters
from rest_framework.permissions import SAFE_METHODS
from rest_framework.viewsets import ModelViewSet

from api.pagination import RecipePagination
from api.permissions import AdminOrReadOnly
from api.serializers import (RecipeReadSerializer,
                             RecipeCreateSerializer,
                             TagSerializer,
                             IngredientSerializer)
from recipes.models import Recipe, Tag, Ingredient, User


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
    # permission_classes = None
    # filter_backends = None
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        user = User.objects.first()
        serializer.save(author=user)
