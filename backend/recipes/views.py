import django_filters.rest_framework
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .custom_pagination import CustomPageNumberPaginator
from users.serializers import FollowRecipeSerializer
from .custom_viewsets import BaseModelViewSet, RecipeModelViewSet
from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Ingredient, Purchase, Recipe, RecipeIngredient,
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
    pagination_class = CustomPageNumberPaginator
    permission_classes = [AdminOrAuthorOrReadOnly, ]
    queryset = Recipe.objects.all()

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
            Favorite,
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
    buying_list = {}
    ingredients = RecipeIngredient.objects.filter(
        recipe__recipes_in_cart__user=request.user
    ).values_list(
        'ingredient__name', 'amount', 'ingredient__measurement_unit'
    )
    ingredients_annotate = ingredients.values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(total_amount=Sum('amount'))

    for ingredient in ingredients_annotate:
        amount = ingredient['total_amount']
        name = ingredient['ingredient__name']
        measurement_unit = ingredient['ingredient__measurement_unit']
        buying_list[name] = {
            'amount': amount,
            'measurement_unit': measurement_unit,
        }

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
