from djoser.serializers import SetPasswordSerializer
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from api.pagination import CustomPagination
from api.permissions import IsRequestUserOrAdminOrHigherOrReadonly
from users.models import FoodgramUser, Follow
from users.serializers import (UserCreateSerializer,
                               UserReadSerializer,
                               FollowSerializer
                               )


class UserViewSet(viewsets.GenericViewSet,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin):
    queryset = FoodgramUser.objects.all()
    permission_classes = [IsRequestUserOrAdminOrHigherOrReadonly, ]  # TODO Добавить свой пермишн
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
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def subscriptions(self, request: Request):
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
        user = request.user
        following = get_object_or_404(FoodgramUser, id=pk)
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
        user = request.user
        following = get_object_or_404(FoodgramUser, id=pk)
        if Follow.objects.filter(following=following, user=user).exists():
            Follow.objects.get(following=following, user=user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            data={'errors': f'Вы не подписаны на пользователя {following}'},
            status=status.HTTP_400_BAD_REQUEST
        )
