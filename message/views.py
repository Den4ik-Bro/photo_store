from itertools import chain
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from .models import Message
from .forms import SendMessageForm

User = get_user_model()


class ViewMessage(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = 'message.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        conversation_id = self.get_object()  # id того с кем открываем переписку
        context = super().get_context_data(object_list=object_list, **kwargs)
        conversationer = User.objects.get(pk=conversation_id.id)
        text_message = Message.objects.select_related('sender', 'receiver').filter(
            sender=conversationer,
            receiver=self.request.user
        )
        text_message_user = Message.objects.select_related('sender', 'receiver').filter(
            sender=self.request.user,
            receiver=conversationer
        )
        message_list = sorted(chain(text_message, text_message_user), key=lambda instance: instance.date_time)
        context['form'] = SendMessageForm()
        context['message_list'] = message_list
        context['conversation_id'] = conversation_id
        return context


class IncomingMessage(LoginRequiredMixin, generic.ListView):
    template_name = 'incoming_message.html'
    paginate_by = 20
    model = Message

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        get_message = Message.objects.select_related('sender', 'receiver').filter(receiver=self.request.user)
        message_dict = {}
        for i in get_message:  # получаем список сообщения каждого отправителя
            message_dict[i.sender] = []
            s = Message.objects.select_related('sender', 'receiver').filter(sender=i.sender, receiver=self.request.user)
            for j in s:
                message_dict[i.sender].append(j)
        context['message_dict'] = message_dict
        return context


class CreateMessage(LoginRequiredMixin, generic.CreateView):
    model = Message
    template_name = 'message.html'
    form_class = SendMessageForm

    def post(self, request, user_id):
        form = self.form_class(request.POST)
        conversationer = User.objects.get(pk=user_id)
        if form.is_valid():
            print('ok')
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.receiver = conversationer
            new_message.save()
            return(redirect(reverse('message:show_messages', kwargs={'pk': user_id})))
        return redirect(reverse('photo_store:index'))  # надо будет над редиректом подумать
