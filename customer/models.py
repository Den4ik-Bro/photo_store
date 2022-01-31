from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_image',
                                      verbose_name='аватар',
                                      blank=True,
                                      null=True,
                                      default='profile_image/default_avatar.png',
                                      )

