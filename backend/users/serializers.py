from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import Recipe

from .models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, following=obj).exists()


class RecipeSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time',
        ]


class ShowFollowsSerializer(UserSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:settings.RECIPES_LIMIT]
        return RecipeSubscriptionSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        queryset = Recipe.objects.filter(following=obj)
        return queryset.count()


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    following = serializers.IntegerField(source='following.id')

    class Meta:
        model = Follow
        fields = [
            'user',
            'following',
        ]

    def validate_following(self, following):
        if (self.context.get('request').method == 'POST'
           and self.context.get('request').user == following):
            raise serializers.ValidationError(
                'Нельзя подписаться самому на себя.')
        return following

    def create(self, validated_data):
        following = validated_data.get('following')
        following = get_object_or_404(
            User, pk=following.get('id')
        )
        user = validated_data.get('user')
        return Follow.objects.create(
            user=user, following=following
        )
