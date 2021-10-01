import django_filters as filters

from .models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = Ingredient
        fields = [
            'name',
            'measurement_unit',
        ]


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )

    class Meta:
        model = Recipe
        fields = [
            'author',
            'tags',
        ]
