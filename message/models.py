from django.contrib.auth import get_user_model
from django.db import models
import datetime
from order.models import Response

User = get_user_model()


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='отправитель')
    text = models.TextField(verbose_name='текст сообщения')
    date_time = models.DateTimeField(verbose_name='дата', default=datetime.datetime.now)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='получатель', related_name='received_messages')
    response = models.ForeignKey(Response, on_delete=models.PROTECT, blank=True, null=True, verbose_name='ответ')

    def __str__(self):
        return f'отправитель {self.sender}, получатель {self.receiver}, время: {self.date_time}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ('-date_time',)
