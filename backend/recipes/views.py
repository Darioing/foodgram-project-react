import django_filters.rest_framework
from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
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
    pagination_class = None


class RecipesViewSet(RecipeModelViewSet):
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend
    ]
    filter_class = RecipeFilter
    pagination_class = PageNumberPagination
    permission_classes = [AdminOrAuthorOrReadOnly, ]

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        is_favorited = self.request.query_params.get('is_favorited')
        shopping_cart = Purchase.objects.filter(
            user=self.request.user.id
        )
        favorite = Favorites.objects.filter(
            user=self.request.user.id
        )

        if is_in_shopping_cart == 'true':
            queryset = queryset.filter(purchase__in=shopping_cart)
        else:
            queryset = queryset.exclude(purchase__in=shopping_cart)
        if is_favorited == 'true':
            queryset = queryset.filter(favorites__in=favorite)
        else:
            queryset = queryset.exclude(favorites__in=favorite)
        return queryset.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadRecipeSerializer
        return RecipeSerializer

    @action(methods=['GET', 'DELETE'],
            url_path='favorite', url_name='favorite',
            permission_classes=[permissions.IsAuthenticated],
            detail=True)
    def favorite(self, request, pk):
        recipe = get_object_or_404(
            Recipe, id=pk
        )
        serializer = FavoriteSerializer(
            data={
                'user': request.user.id,
                'recipe': recipe.id,
            }
        )
        if request.method == 'GET':
            serializer.is_valid(raise_exception=True)
            serializer.save(
                recipe=recipe, user=request.user
            )
            serializer = FollowRecipeSerializer(recipe)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        favorite = get_object_or_404(
            Favorites,
            user=request.user,
            recipe__id=pk
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientsViewSet(BaseModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    pagination_class = None
    filterset_class = IngredientFilter


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def shopping_cart_download_function(request):
    user = request.user
    shopping_cart = user.purchase_set.all()
    buying_list = {}
    for purchase in shopping_cart:
        recipe = purchase.recipe
        recipeingredient = RecipeIngredient.objects.filter(
            recipe=recipe
        )
        for item in recipeingredient:
            amount = item.amount
            name = item.ingredient.name
            measurement_unit = item.ingredient.measurement_unit
            if name not in buying_list:
                buying_list[name] = {
                    'amount': amount,
                    'measurement_unit': measurement_unit,
                }
            else:
                buying_list[name]['amount'] = (
                    buying_list[name]['amount'] + amount
                )
    ingredient_list = []
    for item in buying_list:
        ingredient_list.append(
            f'{item} - {buying_list[item]["amount"]}, '
            f'{buying_list[item]["measurement_unit"]}\n'
        )
    response = HttpResponse(ingredient_list, 'Content-Type: text/plain')
    response['Content-Disposition'] = (
        'attachment;' 'filename="ingredient_list.txt"'
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
            recipe=recipe, user=request.user
        )
        serializer = FollowRecipeSerializer(recipe)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    def delete(self, request, recipe_id):
        user = request.user
        shopping_cart = get_object_or_404(
            Purchase,
            user=user,
            recipe__id=recipe_id,
        )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
