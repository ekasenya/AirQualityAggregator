from django.contrib.auth.models import AbstractUser
from django.db import models

from user.media_utils import get_image_path, OverwriteStorage


class UserProfile(AbstractUser):
    avatar = models.ImageField(null=True, upload_to=get_image_path, storage=OverwriteStorage())
    fields = ('avatar',)
