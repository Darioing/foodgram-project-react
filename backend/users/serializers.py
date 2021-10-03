from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from recipes.models import Recipe
from rest_framework import serializers

from .models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        ]

    def get_is_subscribed(self, obj):

        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, following=obj
        ).exists()


class FollowRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time',
        ]


class ShowFollowSerializer(UserSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        return FollowRecipeSerializer(
            recipes, many=True
        ).data

    def get_recipes_count(self, obj):
        queryset = Recipe.objects.filter(author=obj)
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

    def validate(self, data):

        user = data['user']['id']
        following = data['following']['id']

        if (
            Follow.objects.filter(
                user=user, following__id=following
            ).exists()
        ):
            raise serializers.ValidationError(
                'Вы уже подписаны на данного пользователя')
        elif user == following:
            raise serializers.ValidationError(
                'Вы пытаетесь подписаться на себя'
            )
        return data

    def create(self, validated_data):

        following = validated_data.get('following')
        following = get_object_or_404(
            User, pk=following.get('id')
        )
        user = validated_data.get('user')
        return Follow.objects.create(
            user=user, following=following
        )
