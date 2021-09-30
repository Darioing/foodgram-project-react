from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Follow
from .serializers import FollowSerializer, ShowFollowSerializer

User = get_user_model()


class UserViewSet(UserViewSet):

    @action(
        methods=['GET', 'DELETE'],
        url_path='subscribe', url_name='subscribe',
        permission_classes=[permissions.IsAuthenticated],
        detail=True,)
    def subscribe(self, request, id):
        following = get_object_or_404(
            User, id=id
        )
        user = request.user
        serializer = FollowSerializer(
            data={
                'user': user.id,
                'following': id,
            },
        )
        if request.method == 'GET':
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            serializer = ShowFollowSerializer(following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        paginator = PageNumberPagination()
        paginator.page_size = 6
        page = paginator.paginate_queryset(queryset, request)
        serializer = ShowFollowSerializer(
            page,
            many=True,
            context={
                'user': user
            },
        )
        return paginator.get_paginated_response(serializer.data)
