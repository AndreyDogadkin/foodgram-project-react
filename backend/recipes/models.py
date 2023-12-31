from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from foodgram_backend.constants import (RecipeConstants,
                                        TagConstants,
                                        IngredientConstants,
                                        RecipeIngredientConstants,
                                        )

User = get_user_model()


class Recipe(models.Model):
    """
    Модель рецептов.
    Связи:
        - ingredients --  M2M с моделью Ingredient
            Вспомогательная модель RecipeIngredient
            с указанием количества ингредиентов.
        - tags -- M2M c моделью Tag.
        - author -- Foreign Key с моделью User
    Ограничения:
        - Автор не может создавать рецепты с одинаковыми именами.
        - Время приготовления ограничено минимальным и максимальными значениями
    """

    name = models.CharField(
        max_length=RecipeConstants.MAX_LEN_NAME,
        verbose_name='Название'
    )
    text = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='Ингредиент',
        related_name='recipes',
        through='RecipeIngredient'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=RecipeConstants.MIN_COOKING_TIME,
                message='Минимальное значение "1".'),
            MaxValueValidator(
                limit_value=RecipeConstants.MAX_COOKING_TIME,
                message='Слишком большое значение.')
        ],
        verbose_name='Время приготовления'
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Тег',
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='recipe_name_author_uniq'
            ),
        )
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Модель тегов.
    Ограничения:
        - slug должен быть уникальным.
        - color должен быть предоставлен в формате hex.
            Пример: #0d326e
    """

    name = models.CharField(
        max_length=TagConstants.MAX_LEN_NAME,
        verbose_name='Название',
        unique=True
    )
    color = ColorField(
        max_length=TagConstants.MAX_LEN_COLOR,
        verbose_name='Цветовой код',
        unique=True,
    )
    slug = models.SlugField(
        max_length=TagConstants.MAX_LEN_SLUG,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель ингредиентов.
    Ограничения:
        - Ингредиенты и их ед. измерения не должны повторяться.
    """

    name = models.CharField(
        max_length=IngredientConstants.MAX_LEN_NAME,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=IngredientConstants.MAX_LEN_UNIT,
        verbose_name='Единицы измерения'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='ingredient_unit_uniq'
            ),
        )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Вспомогательная модель для связи рецептов и ингредиентов.
    Связи:
        - recipe -- Foreign Key c моделью Recipe.
        - ingredient -- Foreign Key c моделью Ingredient.
    Ограничения:
        - Количество ограничено минимальным и максимальным значением.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=RecipeIngredientConstants.MIN_AMOUNT,
                message='Минимальное значение "1".'),
            MaxValueValidator(
                limit_value=RecipeIngredientConstants.MAX_AMOUNT,
                message='Слишком большое значение.')],
        default=1,
        verbose_name='Количество'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='recipe_ingredient_uniq'
            ),
        )
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredient.name} -- {self.recipe.name}'


class Favorites(models.Model):
    """
    Модель избранных рецептов.
    Связи:
        - recipe -- Foreign Key c моделью Recipe.
        - user -- Foreign Key c моделью User.
    Ограничения:
        - Рецепты пользователя в избранном не должны повторяться.
    """

    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Избранное',
        related_name='favorites',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        to=User,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=models.CASCADE
    )
    added_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления в избранное',
        editable=False
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='favorite__recipe_user_uniq'
            ),
        )
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.recipe.name} -- {self.user.username}'


class ShoppingList(models.Model):
    """
        Модель списка покупок.
        Связи:
            - recipe -- Foreign Key c моделью Recipe.
            - user -- Foreign Key c моделью User.
        Ограничения:
            - Рецепты пользователя в списке покупок не должны повторяться.
        """

    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Список покупок',
        related_name='shop_list',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        to=User,
        verbose_name='Пользователь',
        related_name='shop_list',
        on_delete=models.CASCADE
    )
    added_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления в список покупок',
        editable=False
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='shop_list__recipe_user_uniq'
            ),
        )
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.recipe.name} -- {self.user.username}'
