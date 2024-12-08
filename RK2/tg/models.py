from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)

class Post(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="posts"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

