import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            RecipeIngredient,
                            Favorites,
                            ShoppingList)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'last_name', )
        read_only_fields = ('__all__', )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_, img_str = data.split(';base64,')
            ext = format_.split('/')[-1]

            data = ContentFile(base64.b64decode(img_str), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вспомогательной модели рецепта
    и ингредиентов с их количеством.
    Используется для вывода ингредиентов в представлении рецептов.
    """

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор представления рецептов.
    """

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer()  # TODO User serializer
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipe_ingredient'
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_extra_field(self, obj, model):
        if not self.context.get('request').user.is_anonymous():
            return model.objects.filter(recipe=obj).exists()
        return False

    def get_is_favorited(self, obj):
        return self.get_extra_field(obj=obj, model=Favorites)

    def get_is_in_shopping_cart(self, obj):
        return self.get_extra_field(obj=obj, model=ShoppingList)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'image',
                  'ingredients', 'cooking_time', 'tags',
                  'author', 'is_favorited', 'is_in_shopping_cart')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вспомогательной модели рецепта
    и ингредиентов с их количеством.
    Используется для создания и обновления рецептов.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientCreateSerializer(
        many=True
    )
    author = UserSerializer(read_only=True)  # TODO USER serializer

    # def validate_tags(self, tags):
    #     ...
    #
    # def validate_ingredients(self, value):
    #     ...

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.update_or_create(
                recipe=recipe, ingredient=ingredient['id'], amount=ingredient['amount']
            )
        return recipe

    def update(self, instance: Recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        if tags:
            instance.tags.clear()
            instance.tags.set(tags)
        if ingredients:
            instance.ingredients.clear()
            for ingredient, amount in ingredients.values():
                RecipeIngredient.objects.update_or_create(
                    recipe=instance, ingredients=ingredient, amount=amount
                )
        return super().update(instance, validated_data)

    def to_representation(self, instance: Recipe):
        response = super().to_representation(instance)
        response['ingredients'] = RecipeIngredientReadSerializer(
            instance.recipe_ingredient.all(), many=True
        ).data
        return response

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time', 'author')
