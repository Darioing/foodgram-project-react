from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import UserSerializer
from .models import (Favorite, Ingredient, Purchase, Recipe, RecipeIngredient,
                     Tag)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'color',
            'slug',
        ]


class FavoriteSerializer(serializers.ModelSerializer):

    user = serializers.IntegerField(source='user.id')
    recipe = serializers.IntegerField(source='recipe.id')

    class Meta:
        model = Favorite
        fields = [
            'user',
            'recipe',
        ]

    def validate(self, data):
        user_id = data['user']['id']
        recipe_id = data['recipe']['id']
        if Favorite.objects.filter(
            user=user_id, recipe__id=recipe_id
        ).exists():
            raise serializers.ValidationError(
                'Нельзя добавить повторно в избранное'
            )
        return data


class PurchaseSerializer(serializers.ModelSerializer):

    user = serializers.IntegerField(source='user.id')
    recipe = serializers.IntegerField(source='recipe.id')

    class Meta:
        model = Purchase
        fields = [
            'user',
            'recipe',
        ]

    def validate(self, data):
        user_id = data['user']['id']
        recipe_id = data['recipe']['id']
        if Purchase.objects.filter(
            user=user_id, recipe__id=recipe_id
        ).exists():
            raise serializers.ValidationError(
                'Вы уже добавили рецепт в корзину'
            )
        return data


class IngredientSerializer(serializers.ModelSerializer):

    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit',
        ]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:

        model = RecipeIngredient
        fields = [
            'id',
            'name',
            'amount',
            'measurement_unit',
        ]


class CreateRecipeIngredientSerializer(RecipeIngredientSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    def to_representation(self, instance):
        ingredient_in_recipe = [
            ingredient for ingredient in
            RecipeIngredient.objects.filter(ingredient=instance)
        ]
        return RecipeIngredientSerializer(ingredient_in_recipe).data


class RecipeSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True,
    )
    ingredients = CreateRecipeIngredientSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'tags',
            'ingredients',
            'image',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'text',
            'cooking_time',
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Purchase.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше минуты'
            )
        return value

    def validate_tags(self, value):
        if len(value) < 1:
            raise serializers.ValidationError(
                'Вы должны указать хотя бы один тег'
            )
        self.unique_validator(value)

        return value

    def validate_ingredients(self, value):
        if len(value) < 1:
            raise serializers.ValidationError(
                'Вы должны выбрать хотя бы один ингредиент'
            )
        for ing in value:
            if ing['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента не должно быть меньше одного'
                )
        self.unique_validator(value)
        return value

    def unique_validator(self, value):
        set_value = len(set(value))
        if set_value != len(value):
            raise serializers.ValidationError(
                'Не должно быть повторений в поле'
            )
        return True

    def create_or_update_cycle(self, recipe, ingredients_data):
        for ingredient in ingredients_data:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            obj, created = RecipeIngredient.objects.get_or_create(
                ingredient=ingredient_id,
                recipe=recipe,
                defaults={'amount': amount}
            )
            if not created:
                obj.amount += amount
                obj.save()

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=request.user, **validated_data
        )
        self.create_or_update_cycle(
            recipe, ingredients_data
        )
        recipe.tags.set(tags_data)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.ingredients.clear()
        self.create_or_update_cycle(
            instance, ingredients_data
        )
        instance.tags.set(tags_data)
        instance.save()
        return instance


class ReadRecipeSerializer(RecipeSerializer):

    tags = TagSerializer(
        read_only=True, many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(
            ingredients, many=True
        ).data
