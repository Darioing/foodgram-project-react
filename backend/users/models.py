from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    def create_user(
        self, email, password, username, first_name, last_name, **kwargs
    ):
        if not email:
            raise ValueError('У пользователя должен быть email адрес')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, password, username, first_name, last_name, **kwargs
    ):
        user = self.create_user(
            email,
            password,
            username,
            first_name,
            last_name,
            **kwargs,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """
    Определяем наш пользовательский класс User.
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    objects = UserManager()
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя',
        help_text='Введите ваше Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия',
        help_text='Введите вашу Фамилию'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Почта',
        help_text='Введите вашу почту')
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',
        help_text='Введите ваш пароль',
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_follow'
            ),
        ]
