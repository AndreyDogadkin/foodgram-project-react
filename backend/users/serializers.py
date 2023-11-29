from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe
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


class FollowRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        source='following.email',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(
        source='following.id',
        read_only=True
    )
    username = serializers.CharField(
        source='following.username',
        read_only=True
    )
    first_name = serializers.CharField(
        source='following.first_name',
        read_only=True
    )
    last_name = serializers.CharField(
        source='following.last_name',
        read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, follow_obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=follow_obj.user,
            following=follow_obj.following
        ).exists()

    def get_recipes_count(self, follow_obj):
        return Recipe.objects.filter(author=follow_obj.following).count()

    def get_recipes(self, follow_obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=follow_obj.following)
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        return FollowRecipeSerializer(recipes, many=True).data

    def validate(self, data):
        following = self.context.get('following')
        user = self.context.get('request').user
        follow_exists = Follow.objects.filter(
            following=following,
            user=user
        ).exists()
        if following == user:
            raise ValidationError('Нельзя подписаться на себя.')
        if follow_exists:
            raise ValidationError(
                f'Вы уже подписаны на пользователя {following}.',
            )
        return data

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_count')
