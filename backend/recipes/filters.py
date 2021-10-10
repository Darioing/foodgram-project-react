import django_filters as filters

from .models import Favorite, Ingredient, Purchase, Recipe


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
    is_favorited = filters.BooleanFilter(
        method='get_favorite'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_in_shopping_cart'
    )

    def get_favorite(self, queryset, name, value):
        user_favorite = Favorite.objects.filter(
            user=self.request.user.id
        )
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == 'true':
            return queryset.filter(favorite__in=user_favorite)
        return queryset.exclude(favorite__in=user_favorite)

    def get_in_shopping_cart(self, queryset, name, value):
        shopping_cart = Purchase.objects.filter(
            user=self.request.user.id
        )
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_in_shopping_cart == 'true':
            return queryset.filter(recipes_in_cart__in=shopping_cart)
        return queryset.exclude(recipes_in_cart__in=shopping_cart)

    class Meta:
        model = Recipe
        fields = [
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags',
        ]
