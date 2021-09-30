from django.contrib import admin
from import_export.admin import ImportMixin

from .models import Favorites, Ingredient, RecipeIngredients, Recipe, Tag
from .resources import IngredientResource


@admin.register(Favorites)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'recipe',
        'user',
    ]


@admin.register(Ingredient)
class IngredientAdmin(ImportMixin, admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'measurement_unit',
    ]
    list_filter = [
        'id',
        'name',
        'measurement_unit',
    ]
    search_fields = ['name', ]
    resource_class = IngredientResource


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'ingredient',
        'recipe',
        'amount',
    ]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'author',
        'name',
    ]
    list_filter = [
        'author',
        'name',
        'tags',
    ]



@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'color',
        'slug',
    ]
