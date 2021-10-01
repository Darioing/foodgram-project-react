from django.contrib import admin

from .models import Follow, User


<<<<<<< HEAD
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'following',
    )


=======
>>>>>>> 4843b895e1fda328e1429f16bb06e8fc474dbff6
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
    )
    list_filter = (
        'email',
        'username',
    )
<<<<<<< HEAD
=======


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'following',
    )
>>>>>>> 4843b895e1fda328e1429f16bb06e8fc474dbff6
