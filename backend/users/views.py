from django.contrib.auth import get_user_model
from rest_framework import filters, permissions
from rest_framework.permissions import AllowAny

from .custom_viewsets import BaseModelViewSet
from .models import Follow
from .serializers import (FollowSerializer, UserRegisterSerializer,
                          UserSerializer)

User = get_user_model()


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'username',
    ]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserRegisterSerializer


class FollowViewSet(BaseModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated, )
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'following__username']

    def get_queryset(self):
        return Follow.objects.filter(following=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
