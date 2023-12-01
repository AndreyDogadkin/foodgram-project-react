from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from api.pagination import CustomPagination
from api.permissions import IsRequestUserOrAdminOrHigherOrReadonly
from users.models import Follow
from users.serializers import (UserCreateSerializer,
                               UserReadSerializer,
                               FollowSerializer
                               )

User = get_user_model()


class UserViewSet(viewsets.GenericViewSet,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin):
    """
    Вьюсет для представления и создания пользователей.
    Права доступа:
        - Просмотр объектов доступен всем пользователям
        - Просмотр конкретного объекта доступен только авторизованным пользователям
        - Создание объектов доступно только авторизованным пользователям
        - Редактирование объектов доступно только авторам или пользователям
        со статусом персонала.
    Доступные методы:
        - GET -- Представление списка пользователей.
        - POST -- Создание пользователя.
        - GET -- Представление пользователя по id.
        - POST -- Изменение пароля.
    Доступные actions:
        - GET -- Представление текущего пользователя.
        - GET -- Представление всех подписок пользователя.
        - POST -- Подписаться на пользователя
        - DELETE -- Отписаться от пользователя
    Пагинация:
        - page=<int> - Номер страницы
        - limit=<int> - Количество объектов на странице(по умолчанию 6)
    """

    queryset = User.objects.all()
    permission_classes = [IsRequestUserOrAdminOrHigherOrReadonly, ]
    pagination_class = CustomPagination
    serializer_class = UserCreateSerializer

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list', 'me']:
            return UserReadSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        elif self.action in ['subscriptions', 'subscribe']:
            return FollowSerializer
        return UserCreateSerializer

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated, ]
    )
    def set_password(self, request: Request):
        """Изменить пароль пользователя."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request: Request):
        """Представление текущего пользователя."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def subscriptions(self, request: Request):
        """Представление всех подписок пользователя."""
        follows = Follow.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(follows)
        serializer = self.get_serializer(
            pages,
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated, ]
    )
    def subscribe(self, request: Request, pk: int):
        """Подписаться на пользователя."""
        user = request.user
        following = get_object_or_404(User, id=pk)
        serializer = self.get_serializer(data=request.data)
        serializer.context['following'] = following
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, following=following)
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request: Request, pk: int):
        """Отписаться от пользователя"""
        user = request.user
        following = get_object_or_404(User, id=pk)
        if Follow.objects.filter(following=following, user=user).exists():
            Follow.objects.get(following=following, user=user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            data={'errors': f'Вы не подписаны на пользователя {following}'},
            status=status.HTTP_400_BAD_REQUEST
        )
