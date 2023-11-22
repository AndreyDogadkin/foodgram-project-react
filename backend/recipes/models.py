from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Recipe(models.Model):
    """Модель рецептов."""

    title = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        upload_to='',  # TODO Заполнить поле upload_to
        verbose_name='Изображение'
    )
    ingredients = models.ManyToManyField(
        'AmountIngredient',
        verbose_name='Ингредиент',
        related_name='recipes',
        through='RecipeAmountIngredient'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(limit_value=1), ],
        verbose_name='Время приготовления'
    )
    tag = models.ManyToManyField(
        'Tag',
        verbose_name='Тег',
        related_name='recipes',
        through='RecipeTag'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=16,
        verbose_name='Название'
    )
    color_code = models.CharField(
        max_length=16,
        verbose_name='Цветовой код'
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


class Ingredient(models.Model):
    """Модель ингредиентов и их единиц измерения."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )


class AmountIngredient(models.Model):
    """Модель ингредиентов и их количества."""

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredients',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(limit_value=1), ],
        verbose_name='Количество')

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'amount'),
                name='ingredient_amount_uniq'
            )
        )
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'


class RecipeTag(models.Model):
    """Вспомогательная модель для связи рецептов и тегов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = (models.UniqueConstraint(
            fields=('recipe', 'tag'),
            name='recipe_tag_uniq'),
        )
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'


class RecipeAmountIngredient(models.Model):
    """Вспомогательная модель для связи рецептов и ингредиентов и их количества."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        AmountIngredient,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = (models.UniqueConstraint(
            fields=('recipe', 'ingredient'),
            name='recipe_ingredient_uniq'),
        )
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецептах'


# TODO Сверить названия полей и максимальное количество символов
# TODO Решить что делать если удалится тег или ингредиент
