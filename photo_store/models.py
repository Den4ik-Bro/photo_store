from django.db import models
from django.contrib.auth.models import User
import datetime


class Photo(models.Model):
    image = models.ImageField(upload_to='photo', verbose_name='фото')
    description = models.TextField(null=True, blank=True, verbose_name='описание фотографии')
    date_time = models.DateTimeField(verbose_name='дата', auto_now=True)
    photographer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='фотограф')
    response = models.ForeignKey('Response', on_delete=models.PROTECT, blank=True, null=True, verbose_name='ответ')
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
    name = models.CharField(max_length=30, verbose_name='имя тэга')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='отправитель')
    text = models.TextField(verbose_name='текст сообщения')
    date_time = models.DateTimeField(verbose_name='дата', default=datetime.datetime.now)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='получатель')
    response = models.ForeignKey('Response', on_delete=models.PROTECT, blank=True, null=True, verbose_name='ответ')

    def __str__(self):
        return f'отправитель {self.sender}, получатель {self.receiver}, время: {self.date_time}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ('-date_time',)


class Order(models.Model):
    date_time = models.DateTimeField(verbose_name='дата', default=datetime.datetime.now)
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, verbose_name='тема_задачи')
    text = models.TextField(blank=True, null=True, verbose_name='описание_задачи')
    price = models.IntegerField(verbose_name='цена')
    is_public = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='клиент')

    def __str__(self):
        return f'Клиент {self.owner}, тема заказа {self.topic}'

    class Meta:
        verbose_name = 'Запрос на съемку'
        verbose_name_plural = 'Запросы на съемку'
        ordering = ('-date_time',)


class Topic(models.Model):
    name = models.CharField(max_length=100, verbose_name='название темы')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'


class Response(models.Model):
    text = models.TextField(verbose_name='текст_отклика')
    datetime = models.DateTimeField(verbose_name='дата', default=datetime.datetime.now)
    is_selected = models.BooleanField()
    rate = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='оценка')
    comment = models.TextField(blank=True, null=True, verbose_name='комментарий')
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name='задача')
    photographer = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='фотограф')

    def __str__(self):
        return f'{self.order}'  # , фотограф {self.photographer}'

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ('-datetime',)
