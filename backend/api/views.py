from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from reportlab.pdfgen import canvas

from api.pagination import RecipePagination
from api.permissions import AdminOrReadOnly
from api.serializers import (RecipeReadSerializer,
                             RecipeCreateSerializer,
                             TagSerializer,
                             IngredientSerializer,
                             FavoritesSerializer,
                             ShoppingListSerializer)
from recipes.models import (Recipe,
                            Tag,
                            Ingredient,
                            RecipeIngredient,
                            User,
                            Favorites,
                            ShoppingList)


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
    # filterset_class = None
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

    @staticmethod
    def __extra_actions(request: Request, serializer, model, pk: int):
        user = User.objects.first()  # TODO Исправить на /user = self.request.user/
        recipe: Recipe = get_object_or_404(Recipe, id=pk)
        object_exists: bool = model.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'POST':
            if object_exists:
                return Response(
                    {'errors': 'Выбранный рецепт уже добавлен.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            obj_serializer = serializer(data=request.data)
            obj_serializer.is_valid(raise_exception=True)
            obj_serializer.save(user=user, recipe=recipe)
            return Response(
                obj_serializer.data,
                status=status.HTTP_201_CREATED)

        if not object_exists:
            return Response(
                data={'errors': 'Выбранный рецепт ранее не был добавлен.'},
                status=status.HTTP_400_BAD_REQUEST)

        model.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        # permission_classes = [],  # TODO Добавить права доступа
    )
    def favorite(self, request: Request, pk: int):
        return self.__extra_actions(
            request=request,
            serializer=FavoritesSerializer,
            model=Favorites,
            pk=pk
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        # permission_classes = [],  # TODO Добавить права доступа
    )
    def shopping_cart(self, request: Request, pk: int):
        return self.__extra_actions(
            request=request,
            serializer=ShoppingListSerializer,
            model=ShoppingList,
            pk=pk
        )

    @action(
        detail=False,
        methods=['get', ],
        # permission_classes = [],  # TODO Добавить права доступа
    )
    def download_shopping_cart(self, request: Request):
        user = User.objects.first()  # TODO Исправить на /user = self.request.user/
        if user.shop_list.exists():
            response = HttpResponse(
                content_type='application/pdf')
            response['Content-Disposition'] = (
                f'attachment; filename="{user.username}_shop_list"'
            )
            shopping_list_pdf = canvas.Canvas(response)
            shopping_list_pdf.setFont('Times-Roman', 50)
            shopping_list_pdf.drawString(
                100,
                500,
                f'{user.username}:')
            shopping_list = RecipeIngredient.objects.filter(
                recipe__shop_list__user=user
            ).values(
                'ingredient__name', 'ingredient__measurement_unit'
            ).annotate(sum_amount=Sum('amount', distinct=True))
            y_coord = 600
            for l_item in shopping_list:
                line = '{} --> {} {}'.format(
                    l_item['ingredient__name'],
                    l_item['sum_amount'],
                    l_item['ingredient__measurement_unit']
                )
                shopping_list_pdf.drawString(x=150, y=y_coord, text=line)
                y_coord += 25
            shopping_list_pdf.showPage()
            shopping_list_pdf.save()
            return response

        return Response(
            data={'errors': 'Список покупок пуст.'},
            status=status.HTTP_400_BAD_REQUEST
        )
