from rest_framework.permissions import SAFE_METHODS
from rest_framework.viewsets import ModelViewSet

from api.serializers import RecipeReadSerializer, RecipeSerializer
from recipes.models import Recipe


class RecipeViewSet(ModelViewSet):

    queryset = Recipe.objects.all()
    # permission_classes = ...
    # filter_backends = ...
    # pagination_class = ...

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeSerializer
