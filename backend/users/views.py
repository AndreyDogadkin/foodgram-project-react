from djoser.serializers import SetPasswordSerializer
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from users.models import FoodgramUser
from users.serializers import UserCreateSerializer, UserReadSerializer


class UserViewSet(viewsets.GenericViewSet,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin):
    queryset = FoodgramUser.objects.all()
    permission_classes = []
    pagination_class = None
    serializer_class = UserCreateSerializer

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list', 'me']:
            return UserReadSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        return UserCreateSerializer

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[]  # TODO Добавить права доступа
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
        permission_classes=[]  # TODO Добавить права доступа
    )
    def me(self, request: Request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

