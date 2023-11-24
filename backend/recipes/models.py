from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    text = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        upload_to='',  # TODO Заполнить поле upload_to
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
            MinValueValidator(limit_value=1,
                              message='Минимальное значение "1".'),
            MaxValueValidator(limit_value=2880,
                              message='Слишком большое значение.')  # TODO Вынести константы
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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=16,
        verbose_name='Название',
        unique=True
    )
    color = models.CharField(
        max_length=16,
        verbose_name='Цветовой код',
        unique=True
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('-name', )


class Ingredient(models.Model):
    """Модель ингредиентов и их единиц измерения."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения'
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='ingredient_unit_uniq'
            ),
        )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class RecipeIngredient(models.Model):
    """Вспомогательная модель для связи рецептов и ингредиентов с их количеством."""

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
            MinValueValidator(limit_value=1,
                              message='Минимальное значение "1".'),
            MaxValueValidator(limit_value=100000,
                              message='Слишком большое значение.')],  # TODO Вынести константы
        default=0,
        verbose_name='Количество'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='recipe_ingredient_uniq'
            ),
            models.UniqueConstraint(
                fields=('recipe', 'amount'),
                name='recipe_amount_uniq'
            )
        )
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'


class Favorites(models.Model):

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

    def __str__(self):
        return f'{self.recipe.name} - {self.user.name}'

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='favorite__recipe_user_uniq'
            ),
        )
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingList(models.Model):

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

    def __str__(self):
        return f'{self.recipe.name} - {self.user.name}'

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='shop_list__recipe_user_uniq'
            ),
        )
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'