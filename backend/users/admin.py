from django.contrib import admin

from .models import Follow, User


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'following',
    ]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
    ]
    list_filter = [
        'email',
        'username',
    ]
