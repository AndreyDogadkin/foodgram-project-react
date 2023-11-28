from rest_framework import viewsets, mixins

from users.models import FoodgramUser
from users.serializers import UserCreateSerializer, UserReadSerializer


class UserViewSet(viewsets.GenericViewSet,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin):
    queryset = FoodgramUser.objects.all()
    permission_classes = []
    pagination_class = None
    serializer_class = UserCreateSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserReadSerializer
        return UserCreateSerializer
