from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from django.core.exceptions import ValidationError


class User(AbstractUser):
    is_photographer = models.BooleanField(default=False, null=True, verbose_name='Если выбрано вы фотограф,'
                                                                                 ' нет - заказчик')


class Photo(models.Model):
    image = models.ImageField(upload_to='photo', verbose_name='фото')
    description = models.TextField(null=True, blank=True, verbose_name='описание фотографии')
    date_time = models.DateTimeField(verbose_name='дата', auto_now=True)
    photographer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='фотограф')
    response = models.ForeignKey('Response', on_delete=models.PROTECT, blank=True, null=True, verbose_name='отклик')
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


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='отправитель')
    text = models.TextField(verbose_name='текст сообщения')
    date_time = models.DateTimeField(verbose_name='дата', default=datetime.datetime.now)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='получатель', related_name='received_messages')
    response = models.ForeignKey('Response', on_delete=models.PROTECT, blank=True, null=True, verbose_name='ответ')

    def __str__(self):
        return f'отправитель {self.sender}, получатель {self.receiver}, время: {self.date_time}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ('-date_time',)


def is_correct_date(date):
    if date < date.today():
        raise ValidationError('Дата не может быть раньше текущей')


class Order(models.Model):
    date_time = models.DateTimeField(verbose_name='дата', default=datetime.datetime.now)
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, verbose_name='тема_задачи')
    text = models.TextField(blank=True, null=True, verbose_name='описание_задачи')
    price = models.IntegerField(verbose_name='цена',
                                validators=(MinValueValidator(1, 'минимальная цена не может быть меньше еденицы'),))
    is_public = models.BooleanField(default=True, verbose_name='публично (фотографии смогут увидеть все)')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='клиент')  # заказчик
    start_date = models.DateField(verbose_name='дата начала', null=True, blank=True, validators=(is_correct_date,))
    finish_date = models.DateField(verbose_name='дата завершения', null=True, blank=True, validators=(is_correct_date,))

    def clean(self):
        if self.start_date > self.finish_date:
            raise ValidationError('Стартовая дата не может быть позже даты окончания заказа')

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
    is_selected = models.BooleanField(blank=True, null=True)
    rate = models.PositiveSmallIntegerField\
        (
            default=0,
            blank=True,
            null=True,
            verbose_name='оценка',
            validators=[MaxValueValidator(10), MinValueValidator(1)]
        )
    comment = models.TextField(blank=True, null=True, verbose_name='комментарий')
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name='задача')
    photographer = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='фотограф')  # исполнитель

    def __str__(self):
        return f'отклик на заказ: {self.order}'  # , фотограф {self.photographer}'

    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
        ordering = ('-datetime',)
