from rest_framework import serializers
from users.models import FoodgramUser, Follow


class UserCreateSerializer(serializers.ModelSerializer):

    @staticmethod
    def validate_username(username):
        if username.lower() == 'me':
            raise serializers.ValidationError(
                f'Недопустимое имя: {username}'
            )
        return username

    def create(self, validated_data):
        return FoodgramUser.objects.create_user(**validated_data)

    class Meta:
        model = FoodgramUser
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password')
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
            "password": {'write_only': True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }


class UserReadSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, following):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(
                user=user,
                following=following
            ).exists()
        return False

    class Meta:
        model = FoodgramUser
        fields = ('email', 'username', 'first_name',
                  'last_name', 'is_subscribed')


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ...
