from rest_framework import serializers

from api.fields import Base64ImageField
from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            RecipeIngredient,
                            Favorites,
                            ShoppingList)
from users.serializers import UserReadSerializer


class TagSerializer(serializers.ModelSerializer):
    """Представление тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Представление ингредиентов."""

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
    Представление рецептов.
    Поля is_favorited и is_in_shopping_cart получены с помощью
    дополнительных методов.
    """

    tags = TagSerializer(many=True, read_only=True)
    author = UserReadSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipe_ingredient'
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_extra_field(self, obj, model):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return model.objects.filter(recipe=obj, user=request.user).exists()

    def get_is_favorited(self, obj):
        return self.get_extra_field(obj=obj, model=Favorites)

    def get_is_in_shopping_cart(self, obj):
        return self.get_extra_field(obj=obj, model=ShoppingList)


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
    """Создание и редактирование рецептов."""

    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
        required=True
    )

    def validate_name(self, name):
        user = self.context.get('request').user
        method = self.context.get('request').method
        if (method == 'POST'
                and Recipe.objects.filter(author=user, name=name).exists()):
            raise serializers.ValidationError(
                f'У вас уже есть рецепт с именем {name}.')
        return name

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Обязательное поле.')
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError('Теги повторятся.')
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError('Обязательное поле.')
        v_ingredients = dict()
        v_ingredients['ids'] = [i.get('id') for i in ingredients if i]
        v_ingredients['amounts'] = [i.get('amount') for i in ingredients if i]
        if len(v_ingredients['ids']) != len(set(v_ingredients['ids'])):
            raise serializers.ValidationError(
                'Ингредиенты повторяются.'
            )
        if len(v_ingredients['ids']) != len(v_ingredients['amounts']):
            raise serializers.ValidationError(
                'Количество указано не у всех ингредиентов.'
            )
        return ingredients

    def add_ingredients(self, recipe, ingredients):
        ingredients.sort(key=lambda x: x['id'].id)
        ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance: Recipe, validated_data: dict):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags:
            instance.tags.clear()
            instance.tags.set(tags)
        else:
            raise serializers.ValidationError({'tags': 'Не указаны.'})
        if ingredients:
            instance.ingredients.clear()
            RecipeIngredient.objects.filter(recipe=instance).delete()
            self.add_ingredients(recipe=instance, ingredients=ingredients)
        else:
            raise serializers.ValidationError({'ingredients': 'Не указаны.'})
        return super().update(instance, validated_data)

    def to_representation(self, instance: Recipe):
        serializer = RecipeReadSerializer(instance)
        return serializer.data


class FavoritesSerializer(serializers.ModelSerializer):
    """Добавление в избранное репрезентации рецептов."""

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
    """Добавления в список покупок репрезентации рецептов."""

    class Meta:
        model = ShoppingList
        fields = ('id', 'name', 'image', 'cooking_time')
