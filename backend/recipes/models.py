from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        help_text='Введите название тега',
        max_length=200,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цвет в HEX',
        help_text='Введите цвет тега в HEX',
        max_length=7,
        null=True,
    )
    slug = models.CharField(
        verbose_name='slug',
        max_length=200,
        unique=True,
        null=True,
    )


class Ingredient(models.Model):

    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единица измерения',
        help_text='Выберите единицу измерения',
    )

    class Meta:
        ordering = ['name']


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes', verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=200, verbose_name='Название рецепта'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Выберите изображение'
    )
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredients',
        verbose_name='Ингредиенты',
        help_text='Укажите ингредиенты и их количество',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления', default=1,
        validators=[
            MinValueValidator(1, 'Значение не может быть меньше 1')
        ]
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Выберите один или несколько тегов'
    )


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_amounts',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_amounts',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество', default=1,
        validators=[
            MinValueValidator(1, 'Значение не может быть меньше 1')
        ]
    )


class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite',
            )
        ]


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,)

    class Meta:
            constraints = [
                models.UniqueConstraint(
                    fields=['user', 'recipe'],
                    name='unique_shopping_cart',
                )
            ]
