import base64

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            RecipeIngredient,
                            Favorites,
                            ShoppingList)
from users.serializers import UserReadSerializer


class Base64ImageField(serializers.ImageField):
    """
    Поле обработки изображений для сериализатора создания рецептов.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_, img_str = data.split(';base64,')
            ext = format_.split('/')[-1]

            data = ContentFile(base64.b64decode(img_str), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор представления тегов.
    """

    @staticmethod
    def validate_color(value):
        try:
            webcolors.normalize_hex(value)
            return value
        except ValueError as e:
            raise serializers.ValidationError(e)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор представления ингредиентов.
    """

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
    author = UserReadSerializer(read_only=True)  # TODO User serializer
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipe_ingredient'
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_extra_field(self, obj, model):
        if not self.context.get('request').user.is_anonymous:
            return model.objects.filter(recipe=obj).exists()
        return False

    def get_is_favorited(self, obj):
        return self.get_extra_field(obj=obj, model=Favorites)

    def get_is_in_shopping_cart(self, obj):
        return self.get_extra_field(obj=obj, model=ShoppingList)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')


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


class RecipeCreateSerializer(RecipeReadSerializer):
    """
    Сериализатор для создания и редактирования рецептов.
    """

    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
        required=True
    )

    @staticmethod
    def validate_tags(tags):
        if not tags:
            raise serializers.ValidationError('Обязательное поле.')
        return tags

    @staticmethod
    def validate_ingredients(ingredients):
        if not ingredients:
            raise serializers.ValidationError('Обязательное поле.')
        validate_ingredients = []
        for ingredient in ingredients:
            if ingredient['id'] in validate_ingredients:
                raise serializers.ValidationError('Ингредиенты повторяются.')
            else:
                validate_ingredients.append(ingredient['id'])
        return ingredients

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

    def update(self, instance: Recipe, validated_data: dict):
        if validated_data.get('tags'):
            tags = validated_data.pop('tags')
            instance.tags.clear()
            instance.tags.set(tags)
        if validated_data.get('ingredients'):
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            for ingredient in ingredients:
                RecipeIngredient.objects.update_or_create(
                    recipe=instance, ingredient=ingredient['id'], amount=ingredient['amount']
                )
        return super().update(instance, validated_data)

    def to_representation(self, instance: Recipe):
        response = super().to_representation(instance)
        response['ingredients'] = RecipeIngredientReadSerializer(
            instance.recipe_ingredient.all(), many=True
        ).data
        response['tags'] = TagSerializer(
            instance.tags.all(), many=True
        ).data
        return response


class FavoritesSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True
    )
    name = serializers.ReadOnlyField(
        source='recipe.name'
    )
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )

    class Meta:
        model = Favorites
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingListSerializer(FavoritesSerializer):

    class Meta:
        model = ShoppingList
        fields = ('id', 'name', 'image', 'cooking_time')
