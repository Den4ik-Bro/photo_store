from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import datetime


User = get_user_model()


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
        return f'Пользователь - {self.owner}, тема -  {self.topic.name}, {self.pk}'

    class Meta:
        verbose_name = 'Запрос на съемку'
        verbose_name_plural = 'Запросы на съемку'
        ordering = ('-date_time',)


class Topic(models.Model):
    TOPICS_CHOICES = (
        ('Свадебная съемка', 'Свадебная съемка'),
        ('Студийная съемка', 'Студийная съемка'),
        ('Детская съемка', 'Детская съемка'),
        ('Контент съемка', 'Контент съемка'),
        ('Лав стори', 'Лав стори'),
        ('Прогулка', 'Прогулка'),
        ('Другое', 'Другое'),
    )
    name = models.CharField(max_length=100, verbose_name='название темы', choices=TOPICS_CHOICES)

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