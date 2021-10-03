from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from colorfield.fields import ColorField

User = get_user_model()


class Tag(models.Model):
    """
    Модель тэгов
    """

    name = models.CharField(
        verbose_name='Название',
        help_text='Введите тег',
        max_length=200,
        unique=True,
    )
    color = ColorField(
        verbose_name='Тег в HEX формате',
        help_text='Введите цвет тега в HEX формате',
        max_length=7,
        null=True,
    )
    slug = models.CharField(
        verbose_name='slug',
        max_length=200,
        unique=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Ingredient(models.Model):
    """
    Модель ингредиентов
    """

    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент',
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единица измерения',
        help_text='Выберите единицу измерения',
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'


class Recipe(models.Model):
    """
    Модель рецептов
    """

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        verbose_name='Картинка рецепта',
        help_text='Выберите изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления', default=1,
        validators=[
            MinValueValidator(1, 'Значение не может быть меньше 1')
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        verbose_name='Ингредиенты рецепта',
        help_text='Выберите ингредиент и его массу',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'


class Favorite(models.Model):
    """
    Модель избранного
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'user',
                    'recipe',
                ],
                name='unique_favorite',
            )
        ]


class Purchase(models.Model):
    """
    Модель покупок
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Purchase'
        verbose_name_plural = 'Purchases'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'user',
                    'recipe',
                ],
                name='unique_shopping_cart',
            )
        ]


class RecipeIngredient(models.Model):
    """
    Дополнительная модель для связи ManyToMany
    ингредиентов рецепта
    """

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        default=1,
        validators=[
            MinValueValidator(
                1, 'Значение не может быть меньше 1'
            )
        ]
    )

    class Meta:
        verbose_name = 'Recipe Ingredient'
        verbose_name_plural = 'Recipe Ingredients'
