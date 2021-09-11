from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FollowViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='Users')
router.register('follows', FollowViewSet, basename='Follows')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('router')),
]
