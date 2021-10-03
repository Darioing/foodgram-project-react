from django.contrib import admin

from import_export.admin import ImportMixin

from .models import Favorite, Ingredient, Recipe, RecipeIngredient, Tag
from .resources import IngredientResource


@admin.register(Favorite)
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


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'recipe',
        'ingredient',
        'amount',
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'color',
        'slug',
    ]
