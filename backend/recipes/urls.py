from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, RecipesViewSet, ShoppingCartView,
                    TagsViewSet, shopping_cart_download_function)

router = DefaultRouter()
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')


urlpatterns = [
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartView.as_view(),
        name='shopping_cart',
    ),
    path(
        'recipes/download_shopping_cart/',
        shopping_cart_download_function,
        name='download_shopping_cart',
    ),
    path('', include(router.urls)),
]
