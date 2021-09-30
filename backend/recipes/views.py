import django_filters.rest_framework
from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializers import FollowRecipeSerializer

from .custom_viewsets import BaseModelViewSet, RecipeModelViewSet
from .filters import IngredientFilter, RecipeFilter
from .models import (Favorites, Ingredient, Purchase, Recipe, RecipeIngredient,
                     Tag)
from .permissions import AdminOrAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          PurchaseSerializer, ReadRecipeSerializer,
                          RecipeSerializer, TagSerializer)

User = get_user_model()


class TagsViewSet(BaseModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]


class RecipesViewSet(RecipeModelViewSet):

    filter_class = RecipeFilter
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend
    ]
    permission_classes = [AdminOrAuthorOrReadOnly, ]
    pagination_class = PageNumberPagination

    def get_queryset(self):

        queryset = Recipe.objects.all()
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        is_favorited = self.request.query_params.get('is_favorited')
        user = self.request.user.id
        shopping_cart = Purchase.objects.filter(user=user)
        favorite = Favorites.objects.filter(user=user)

        if is_in_shopping_cart == 'true':
            queryset = queryset.filter(
                purchase__in=shopping_cart
            )
        else:
            queryset = queryset.exclude(
                purchase__in=shopping_cart
            )
        if is_favorited == 'true':
            queryset = queryset.filter(
                favorites__in=favorite
            )
        else:
            queryset = queryset.exclude(
                favorites__in=favorite
            )
        return queryset.all()

    def get_serializer_class(self):

        if self.request.method == 'GET':
            return ReadRecipeSerializer
        return RecipeSerializer

    @action(methods=['GET', 'DELETE'],
            url_path='favorite',
            url_name='favorite',
            permission_classes=[permissions.IsAuthenticated],
            detail=True)
    def favorite(self, request, id):

        recipe = get_object_or_404(
            Recipe, id=id
        )
        user = request.user
        serializer = FavoriteSerializer(
            data={
                'user': user.id,
                'recipe': recipe.id,
            }
        )
        if request.method == 'GET':
            serializer.is_valid(raise_exception=True)
            serializer.save(
                recipe=recipe, user=user
            )
            serializer = FollowRecipeSerializer(recipe)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        favorite = get_object_or_404(
            Favorites,
            user=user,
            recipe__id=id,
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientsViewSet(BaseModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    permission_classes = [AllowAny, ]


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def shopping_cart_download_function(request):

    user = request.user
    shopping_cart = user.purchase_set.all()
    ingredient_list = {}
    for purchase in shopping_cart:
        ingredients = RecipeIngredient.objects.filter(
            recipe=purchase.recipe
        )
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name in ingredient_list:
                ingredient_list[name]['amount'] = (
                    ingredient_list[name]['amount'] + amount
                )
            else:
                ingredient_list[name] = {
                    'amount': amount,
                    'measurement_unit': measurement_unit,
                }
    purchases = []
    for ingredient in ingredient_list:
        purchases.append(
            f'{ingredient} - {ingredient_list[ingredient]["amount"]}, '
            f'{ingredient_list[ingredient]["measurement_unit"]}\n'
        )
    response = HttpResponse(
        purchases, 'Content-Type: text/plain'
    )
    response['Content-Disposition'] = (
        'attachment;' 'filename="purchases.txt"'
    )
    return response


class ShoppingCartView(APIView):

    http_method_names = ['get', 'delete']
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, recipe_id):

        user = request.user
        recipe = get_object_or_404(
            Recipe, id=recipe_id
        )
        serializer = PurchaseSerializer(
            data={
                'user': user.id,
                'recipe': recipe.id,
            },
            context={
                'request': request
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(
            recipe=recipe, user=user
        )
        serializer = FollowRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):

        shopping_cart = get_object_or_404(
            Purchase,
            user=request.user,
            recipe__id=recipe_id,
        )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
