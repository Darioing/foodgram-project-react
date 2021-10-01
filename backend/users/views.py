from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Follow
from .serializers import FollowSerializer, ShowFollowsSerializer

User = get_user_model()


class UserViewSet(UserViewSet):

    @action(
        methods=['GET', 'DELETE'],
        url_path='subscribe', url_name='subscribe',
        permission_classes=[permissions.IsAuthenticated],
        detail=True,)
    def subscribe(self, request, id):
<<<<<<< HEAD
        following = get_object_or_404(User, id=id)
=======
        following = get_object_or_404(
            User, id=id
        )
        user = request.user
>>>>>>> 4843b895e1fda328e1429f16bb06e8fc474dbff6
        serializer = FollowSerializer(
            data={
                'user': request.user.id,
                'following': id,
            }
        )
        if request.method == 'GET':
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            serializer = ShowFollowsSerializer(following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
<<<<<<< HEAD
        get_object_or_404(Follow, user=request.user, following__id=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['GET'],
        url_path='subscriptions', url_name='subscriptions',
        permission_classes=[permissions.IsAuthenticated],
    )
    def show_follows(self, request):

        queryset = User.objects.filter(following__user=request.user)
=======
        get_object_or_404(
            Follow,
            user=user,
            following__id=id,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET', ],
            url_path='subscriptions', url_name='subscriptions',
            permission_classes=[permissions.IsAuthenticated],
            detail=False,)
    def show_follow(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
>>>>>>> 4843b895e1fda328e1429f16bb06e8fc474dbff6
        paginator = PageNumberPagination()
        paginator.page_size = 6
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ShowFollowsSerializer(
            result_page,
            many=True,
            context={
                'user': request.user,
            },
        )
        return paginator.get_paginated_response(serializer.data)
