from django.contrib.auth import get_user_model
from django.db import models
from order.models import Response

User = get_user_model()


class Photo(models.Model):
    image = models.ImageField(upload_to='photo', verbose_name='фото')
    description = models.TextField(null=True, blank=True, verbose_name='описание фотографии')
    date_time = models.DateTimeField(verbose_name='дата', auto_now=True)
    photographer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='фотограф')
    response = models.ForeignKey(Response, on_delete=models.PROTECT, blank=True, null=True, verbose_name='отклик')
    tags = models.ManyToManyField('Tag', verbose_name='имя тэга', blank=True)

    def __str__(self):
        return f'{self.photographer.first_name} {self.photographer.last_name} Фотография № {self.id}'

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'
        ordering = ('-date_time',)


# class TagPhoto(models.Model):
#     tag_id = models.IntegerField()
#     photo_id = models.IntegerField()


class Tag(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name='имя тэга',
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'






