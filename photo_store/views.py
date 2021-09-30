import datetime
from itertools import chain
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from .models import Photo, Message, Order, Topic, Response, Tag
from django.db.models import Q, Prefetch, Avg, Count
from .forms import ProfileForm, OrderForm, ResponseForm, PhotoForm, SendMessageForm, RegistrationUserForm, TagForm, \
    RateResponseForm, InviteForm
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model, authenticate, login
from django.forms import modelformset_factory, formset_factory
from django.views import generic
from django.core.mail import send_mail
from .serializers import OrderSerializer, ResponseSerializer, MessageSerializer, ShowMessageSerializer, \
    ExtendOrderSerializer
import json
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.decorators import api_view
from rest_framework.response import Response


from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


if not Permission.objects.filter(codename='can_execute').exists():
    content_type = ContentType.objects.get_for_model(Order)
    can_execute_permission = Permission.objects.create(
        codename='can_execute',
        name='can execute order',
        content_type=content_type
    )

User = get_user_model()


class MainView(generic.TemplateView):
    template_name = 'main.html'


# def main(request):
#     """Главная страница"""
#     return render(request, 'main.html')


def profile_login(request):
    """редирект на profile/<int:user_id>/"""
    return redirect(reverse('photo_store:show_profile', kwargs={'pk': request.user.id}))


class TestMessage(generic.DetailView):
    model = User
    template_name = 'test_message.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['photo_form'] = PhotoForm()
        context['message_form'] = SendMessageForm()
        # message_list = Message.objects.select_related('sender', 'receiver')\
        # .filter(Q(receiver=self.request.user) | Q(sender=self.request.user))
        get_message = Message.objects.select_related('sender', 'receiver').filter(receiver=self.request.user)
        message_dict = {}
        for i in get_message:   # получаем список сообщения каждого отправителя
            user_receiver_list = Message.objects.select_related('sender', 'receiver')\
                .filter(sender=i.sender, receiver=self.request.user)

            user_sender_list = Message.objects.select_related('sender', 'receiver')\
                .filter(sender=self.request.user, receiver=i.sender)
            message_list = sorted(chain(user_receiver_list, user_sender_list),
                                  key=lambda instance: instance.date_time,
                                  reverse=True)
            print(message_list)
            print('STOP')
            """
            message_list - список всех сообщений где request.user получатель и отправитель с тем с кем переписывается
            """
            message_dict[i.sender] = message_list  # и добовляем этот скписок в словарь по ключу, где ключ это имя собеседника
            # for j in user_receiver_list:
            #     message_dict[i.sender].append(j)
        context['message_dict'] = message_dict
        return context


class ProfileDetailView(generic.DetailView):
    model = User
    template_name = 'profile.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return super().get_queryset().prefetch_related\
        (
            Prefetch('order_set', Order.objects.select_related('topic', 'owner').filter(owner=self.request.user))
        )\
        .prefetch_related\
        (
            Prefetch('response_set', Response.objects.select_related('photographer', 'order').filter(photographer=self.request.user))
        )\
        .prefetch_related\
        (
            Prefetch('received_messages', Message.objects.select_related('sender', 'receiver').all())
        )\
        .annotate(avg_rate=Avg('response__rate')).get(pk=pk)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['photo_form'] = PhotoForm()
        context['message_form'] = SendMessageForm()
        get_message = Message.objects.select_related('sender', 'receiver').filter(receiver=self.request.user)
        message_dict = {}
        for i in get_message:   # получаем список сообщения каждого отправителя
            message_dict[i.sender] = []
            s = Message.objects.select_related('sender', 'receiver').filter(sender=i.sender, receiver=self.request.user)
            for j in s:
                message_dict[i.sender].append(j)
        context['message_dict'] = message_dict
        return context


class PhotoCreateView(generic.CreateView):
    model = User

    def post(self, request, *args, **kwargs):
        photo_form = PhotoForm(request.POST, request.FILES)
        if photo_form.is_valid():
            photo = photo_form.save(commit=False)
            photo.photographer = self.request.user
            photo.save()
            return redirect(reverse('photo_store:show_profile', kwargs={'pk': self.request.user.id}))


# def profile(request, user_id):
#     """функция профиля"""
#     user = User.objects.prefetch_related\
#         (
#             Prefetch('order_set', Order.objects.select_related('topic', 'owner').filter(owner=request.user))
#         )\
#         .prefetch_related\
#         (
#             Prefetch('response_set', Response.objects.select_related('photographer', 'order').filter(photographer=request.user))
#         )\
#         .prefetch_related\
#         (
#             Prefetch('received_messages', Message.objects.select_related('sender', 'receiver').all())
#         )\
#         .annotate(avg_rate=Avg('response__rate')).get(pk=user_id)
#     """ниже попытка оптимизировать запрос"""
#     # user = User.objects.prefetch_related\
#     # (
#     #     Prefetch('order_set', Order.objects.select_related('topic', 'owner').filter(owner=request.user))
#     # )\
#     # .prefetch_related\
#     # (
#     #     Prefetch
#     #     (
#     #         'response_set', Response.objects.prefetch_related
#     #         (
#     #         Prefetch
#     #             (
#     #             'photographer', User.objects.prefetch_related
#     #                 (
#     #             Prefetch
#     #                     (
#     #                 'order_set', Order.objects.select_related('topic', 'owner').filter(owner=request.user)
#     #                     )
#     #                 )
#     #             )
#     #         )
#     #     )
#     # )\
#     # .annotate(avg_rate=Avg('response__rate')).get(pk=user_id)
#     get_message = Message.objects.select_related('sender', 'receiver').filter(receiver=user)
#     message_dict = {}
#     for i in get_message:   # получаем список сообщения каждого отправителя
#         message_dict[i.sender] = []
#         s = Message.objects.select_related('sender', 'receiver').filter(sender=i.sender, receiver=user)
#         for j in s:
#             message_dict[i.sender].append(j)
#             # message_dict[i.sender].append(j.id)
#     if request.method == 'POST':
#         message_form = SendMessageForm(request.POST)
#         photo_form = PhotoForm(request.POST, request.FILES)
#         if photo_form.is_valid():
#             photo = photo_form.save(commit=False)
#             photo.photographer = request.user
#             photo.save()
#             return redirect(reverse('photo_store:show_profile', kwargs={'user_id': request.user.id}))
#         if message_form.is_valid():
#             message = message_form.save(commit=False)
#             message.sender = request.user
#             message.receiver = User.objects.get(id=user_id)
#             message.save()
#             return redirect(reverse('photo_store:show_profile', kwargs={'user_id': request.user.id}))
#     photo_form = PhotoForm()
#     message_form = SendMessageForm()
#     return render(request, 'profile.html', {
#         'user': user,
#         'photo_form': photo_form,
#         'message_form': message_form,
#         'message_dict': message_dict
#     })


# def profile(request, user_id):
#     """Страница профиля"""
#     user = User.objects.get(id=user_id)
#     photos = Photo.objects.filter(photographer=user)
#     message = Message.objects.filter(Q(sender=user) | Q(receiver=user))  # Q | = или
#     response = Response.objects.filter(photographer=user)
#     my_orders = Order.objects.filter(owner=user)
#     if request.method == 'POST':
#         photo_form = PhotoForm(request.POST, request.FILES)
#         if photo_form.is_valid():
#             photo = photo_form.save(commit=False)
#             photo.photographer = request.user
#             photo.save()
#             return redirect('/profile/' + str(user.id) + '/')
#     photo_form = PhotoForm()
#     if request.method == 'POST':
#         message_form = SendMessageForm(request.POST)
#         if message_form.is_valid():
#             message = message_form.save(commit=False)
#             message.sender = request.user
#             message.receiver = User.objects.get(id=user_id)
#             message.save()
#             return redirect('/profile/' + str(user.id) + '/')
#     message_form = SendMessageForm()
#     return render(request, 'profile.html', {'current_user': user,
#                                             'user_photos': photos,
#                                             'user_message': message,
#                                             'user_response': response,
#                                             'photo_form': photo_form,
#                                             'my_orders': my_orders,
#                                             'message_form': message_form})


class EditProfileView(generic.UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'edit_profile.html'

    def get_success_url(self):
        return reverse('photo_store:show_profile', kwargs={'pk': self.request.user.id})

    def get(self, request, pk):
        if pk != request.user.id:
            return redirect(reverse('photo_store:show_profile', kwargs={'pk': request.user.id}))
        return super().get(request, pk)

    def post(self, request, pk):
        if pk != request.user.id:
            return redirect(reverse('photo_store:show_profile', kwargs={'pk': request.user.id}))
        return super().post(request, pk)

# def edit_profile(request, user_id):
#     """редактирование профиля"""
#     if user_id != request.user.id:
#         return redirect(reverse('photo_store:show_profile', kwargs={'user_id': request.user.id}))
#     user = request.user
#     form = ProfileForm(instance=user)
#     if request.method == 'POST':
#         form = ProfileForm(request.POST, instance=user)
#         if form.is_valid():
#             user.save()
#             return redirect(reverse('photo_store:show_profile', kwargs={'user_id': request.user.id}))
#     return render(request, 'edit_profile.html', {
#         'profile_form': form
#     })


class DeletePhotoView(generic.DeleteView):
    model = Photo

    def get_success_url(self):
        return reverse('photo_store:show_profile', kwargs={'pk': self.request.user.id})

    def get(self, request, pk):
        return self.post(request, pk)


# def del_photo(request, photo_id):
#     """Функция удаления фотографии. Комментарий от Леонида"""
#     # if request.method == 'POST':
#     user = request.user
#     photo = Photo.objects.get(id=photo_id)
#     photo.delete()
#     return redirect(reverse('photo_store:show_profile', kwargs={'user_id': user.id})) # '/profile/' + str(user.id) + '/'


class PhotographersListView(generic.ListView):
    model = User
    context_object_name = 'user'
    template_name = 'photographers.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        InviteFormSet = modelformset_factory(User, InviteForm, extra=0)
        context['form_set'] = InviteFormSet(queryset=User.objects.filter(is_photographer=True)
                                 .exclude(pk=self.request.user.id)
                                 .annotate(avg_rate=Avg('response__rate')), form_kwargs={'owner': self.request.user})
        return context


# def photographers(request):
#     """список пользователей которые являются фотографами"""
#     InviteFormSet = modelformset_factory(User, InviteForm, extra=0)
#     form_set = InviteFormSet(queryset=User.objects.filter(is_photographer=True)
#                              .exclude(pk=request.user.id)
#                              .annotate(avg_rate=Avg('response__rate')), form_kwargs={'owner': request.user})
#     return render(request, 'photographers.html', {
#         'form_set': form_set
#       })


class InviteToOrders(generic.CreateView):
    model = Order

    def post(self, request, *args, **kwargs):
        InviteFormSet = modelformset_factory(User, InviteForm, extra=0)
        form_set = InviteFormSet(request.POST, form_kwargs={'owner': request.user})
        # print(form_set)
        if form_set.is_valid():
            # instances = form_set.save(commit=False)
            mail_list = []
            for form in form_set:
                receiver = form.cleaned_data['id']
                order = form.cleaned_data['orders']
                if order:
                    order_url = reverse('photo_store:order', kwargs={'pk': order.id})
                    text_message = f'{request.user} приглащает вас на съемку <a href="{order_url}">{order}</a>'
                    Message.objects.create(
                        receiver=receiver,
                        sender=request.user,
                        text= text_message
                    )
                    if receiver.email:
                        mail_list.append(receiver.email)
            send_mail('Photo_store: Вас пригласили в заказ!',
                      text_message, 'admin@photo_store.ru',
                      mail_list)
            return redirect(reverse('photo_store:show_profile', kwargs={'pk': self.request.user.id}))
        else:
            return redirect(reverse('photo_store:photographers'))


# def invite_to_orders(request):
#     if request.method == 'POST':
#         InviteFormSet = modelformset_factory(User, InviteForm, extra=0)
#         form_set = InviteFormSet(request.POST, form_kwargs={'owner': request.user})
#         if form_set.is_valid():
#             print('ok')
#             # for form in form_set:
#             #     receiver = form.cleaned_data["id"]
#             #     order = form.cleaned_data["orders"]
#             #     order_url = reverse('photo_store:order', kwargs={'order_id': order.id})
#             #     Message.objects.create(
#             #         receiver=receiver,
#             #         sender=request.user,
#             #         text=f'{request.user} приглащает вас на съемку <a href="{order_url}">{order}</a>'
#             #     )
#             return redirect(reverse('photo_store:show_profile', kwargs={'pk': request.user.id}))
#         else:
#             print(form_set.errors)
#     return redirect(reverse('photo_store:photographers'))


class ViewMessage(generic.DetailView):
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


class CreateMessage(generic.CreateView):
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
            return(redirect(reverse('photo_store:show_messages', kwargs={'pk': user_id})))
        return redirect(reverse('photo_store:index'))  # надо будет над редиректом подумать


# def view_message(request, conversationer_id):
#     """посмотреть переписку"""
#     conversationer = User.objects.get(pk=conversationer_id)
#     text_message = Message.objects.select_related('sender', 'receiver').filter(
#         sender=conversationer,
#         receiver=request.user
#     )
#     text_message_user = Message.objects.select_related('sender', 'receiver').filter(
#         sender=request.user,
#         receiver=conversationer
#     )
#     message_list = sorted(chain(text_message, text_message_user), key=lambda instance: instance.date_time)
#     form = SendMessageForm()
#     if request.method == 'POST':
#         form = SendMessageForm(request.POST)
#         if form.is_valid():
#             new_message = form.save(commit=False)
#             new_message.sender = request.user
#             new_message.receiver = conversationer
#             new_message.save()
#             return redirect(reverse('photo_store:show_messages',  # '/message/' + str(conversationer_id) + '/'
#                                     kwargs={'conversationer_id': conversationer_id}))
#     return render(request, 'message.html', {
#         'message_list': message_list,
#         'form': form
#     })


# def orders_test(request):
#     """работа с формсетом, тестовая функция"""
#     orders = Order.objects.only('topic', 'owner',)\
#         .select_related('owner', 'topic')\
#         .exclude(owner=request.user)\
#         .all()
#     OrderFormSet = modelformset_factory(Order, exclude=('date_time', 'owner'), extra=3)
#     if request.method == 'POST':
#         formset = OrderFormSet(request.POST)
#         orders = []
#         if formset.is_valid():
#             instances = formset.save(commit=False)
#             for instance in instances:
#                 instance.owner = request.user
#                 orders.append(instance)
#             Order.objects.bulk_create(orders)
#             return redirect(reverse('photo_store:profile'))
#     formset = OrderFormSet(queryset=Order.objects.none())
#     return render(request, 'orders_test.html', {
#         'user_orders': orders,
#         'formset': formset
#     })


class OrderListView(generic.ListView):
    # model = Order
    queryset = Order.objects.only('topic', 'owner',)\
        .select_related('owner', 'topic')\
        .all()
    template_name = 'orders.html'
    context_object_name = 'user_orders'

    def get_queryset(self):
        return super().get_queryset().exclude(owner=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        OrderFormSet = modelformset_factory(Order, exclude=('date_time', 'owner'), extra=3)
        context['formset'] = OrderFormSet(queryset=Order.objects.none())
        context['ajax_form'] = OrderForm()
        return context


class OrderCreateView(generic.CreateView):
    model = Order
    # form_class = OrderForm

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('photo_store.add_order'):
            print('NO')
            return redirect(reverse('photo_store:profile'))
        OrderFormSet = modelformset_factory(Order, exclude=('date_time', 'owner'), extra=3)
        formset = OrderFormSet(request.POST)
        orders = []
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.owner = request.user
                orders.append(instance)
            Order.objects.bulk_create(orders)
            return redirect(reverse('photo_store:profile'))
        return render(request, 'orders.html', {'user_orders': Order.objects.only('topic', 'owner',)\
                                                                        .select_related('owner', 'topic')\
                                                                        .all().exclude(owner=request.user),
                                               'formset': formset})


# def orders(request):
#     """Заказы"""
#     orders = Order.objects.only('topic', 'owner',)\
#         .select_related('owner', 'topic')\
#         .exclude(owner=request.user)\
#         .all()
#     form = OrderForm()
#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             order = form.save(commit=False)
#             order.owner = request.user
#             order.save()
#             return redirect(reverse('photo_store:show_profile', kwargs={'user_id': request.user.id}))
#     return render(request, 'orders.html', {
#         'user_orders': orders,
#         'form': form
#     })


# def add_order(request):
#     if request.method == 'POST':
#         text = request.POST['description']
#         price = request.POST['price']
#         is_public = True if 'is_public' in request.POST else False
#         topic = Topic.objects.get(id=request.POST['topic_id'])
#         order = Order.objects.create(text=text,
#                                      price=price,
#                                      is_public=is_public,
#                                      topic=topic,
#                                      owner=request.user)
#     return redirect('/orders/')


class GetOrderDetailView(generic.DetailView):
    model = Order
    template_name = 'order_info.html'
    context_object_name = 'current_order'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        form = ResponseForm()
        photo_form = PhotoForm()
        rate_response_form = RateResponseForm()
        order = self.get_object()
        is_user_has_response = order.response_set.filter(photographer=self.request.user).exists()
        accepted_response = order.response_set.filter(is_selected=True).first()
        context['form'] = form
        context['ajax_form'] = ResponseForm()
        context['photo_form'] = photo_form
        context['rate_response_form'] = rate_response_form
        context['is_user_has_response'] = is_user_has_response
        context['accepted_response'] = accepted_response
        if accepted_response:
            photos = Photo.objects.select_related('response', 'photographer').filter(response=accepted_response)
            context['photo_list'] = photos
            print(photos)
        else:
            photos = Photo.objects.only('image').order_by('?').filter(response__isnull=False)
            context['photo_list'] = photos[:1]
        return context


# def get_order(request, order_id):
#     """просмотр заказа и добавление отклика на заказ"""
#     order = Order.objects.only('topic', 'owner', 'price', 'text')\
#                         .select_related('topic', 'owner')\
#                         .prefetch_related\
#                             (
#                                 Prefetch
#                                     (
#                                         'response_set',
#                                         Response.objects.prefetch_related
#                                             (
#                                                 Prefetch
#                                                     (
#                                                         'photographer',
#                                                         User.objects.filter(is_photographer=True)\
#                                                                     .prefetch_related
#                                                                         (
#                                                                             Prefetch
#                                                                                 (
#                                                                                     'response_set',
#                                                                                     Response.objects.filter(is_selected=True)
#                                                                                  )
#                                                                         )
#                                                                     .annotate(avg_rate=Avg('response__rate')))
#                                             ))
#                             )\
#                         .get(pk=order_id)
#     is_user_has_response = order.response_set.filter(photographer=request.user).exists()
#     accepted_response = order.response_set.filter(is_selected=True).first()
#     # rate_photographer = Response.objects.filter(photographer=user).aggregate(Avg('rate')) средний рейтинг фотографа
#     if request.method == 'POST':  # добавить отклик
#         form = ResponseForm(request.POST) # order_info.html, string 9
#         photo_form = PhotoForm(request.POST, request.FILES) # order_info.html, string 82
#         rate_response_form = RateResponseForm(request.POST) # order_info.html, string 36
#         if form.is_valid():                             # добавить отклик
#             response = form.save(commit=False)
#             response.order = order
#             response.photographer = request.user
#             response.is_selected = False
#             response.save()
#             Message.objects.create(text=response.text,   # сообщение заказчику от исполнителя
#                                    sender=response.photographer,
#                                    receiver=order.owner)
#             return redirect(reverse('photo_store:response sent'))
#         if photo_form.is_valid():                        # добавить фотку к заказу
#             photo = photo_form.save(commit=False)
#             photo.photographer = request.user
#             photo.response = order.response_set.get(is_selected=True)
#             photo.save()
#             return redirect(reverse('photo_store:order', kwargs={'pk': order.id})) # '/order/' + str(order.id) + '/'
#         if rate_response_form.is_valid():                 # добавить оценку и отзыв выполненого заказа
#             rate_comment = rate_response_form.save(commit=False)
#             accepted_response.comment = rate_comment.comment
#             accepted_response.rate = rate_comment.rate
#             accepted_response.save()
#             return redirect(reverse('photo_store:order', kwargs={'pk': order.id}))
#     form = ResponseForm()
#     photo_form = PhotoForm()
#     rate_response_form = RateResponseForm()
#     context = {'current_order': order,
#                'is_user_has_response': is_user_has_response,
#                'accepted_response': accepted_response,
#                'form': form,
#                'photo_form': photo_form,
#                'rate_response_form': rate_response_form}
#     if accepted_response:
#         photos = Photo.objects.select_related('response', 'photographer').filter(response=accepted_response)
#         context['photo_list'] = photos
#         print(photos)
#     else:
#         photos = Photo.objects.only('image').order_by('?').filter(response__isnull=False)
#         #  user.response_set.aggregate(Avg('rate')))
#         context['photo_list'] = photos[:1]
#         # context['rate'] =
#     return render(request, 'order_info.html', context)


class CreateResponse(generic.CreateView):
    model = Response
    template_name = 'order_info.html'

    def post(self, request, pk):
        form = ResponseForm(request.POST)
        order = Order.objects.get(pk=pk)
        if form.is_valid():
            response = form.save(commit=False)
            response.order = order
            response.photographer = request.user
            response.is_selected = False
            response.save()
            Message.objects.create(text=response.text,   # сообщение заказчику от исполнителя
                                   sender=response.photographer,
                                   receiver=order.owner)
            send_mail(
                'Photo_Store: информация по заказу ' + str(order),
                'На ваш заказ откликнулся ' + str(response.photographer),
                'admin@photo_store.ru',
                [order.owner.email]
            )
            # return redirect(reverse('photo_store:order', kwargs={'pk': order.id}))
        return redirect(reverse('photo_store:order', kwargs={'pk': order.id}))


class CreateRateResponse(generic.CreateView):
    model = Response
    template_name = 'order_info.html'

    def post(self, request, pk):
        order = Order.objects.get(pk=pk)
        rate_response_form = RateResponseForm(request.POST)
        for response in order.response_set.all():
            if response.is_selected == True:
                current_response = response
        if rate_response_form.is_valid():
            rate_comment = rate_response_form.save(commit=False)
            current_response.comment = rate_comment.comment
            current_response.rate = rate_comment.rate
            current_response.save()
            return redirect(reverse('photo_store:order', kwargs={'pk': order.id}))
        else:
            return redirect(reverse('photo_store:order', kwargs={'pk': order.id}))


class CreateResponsePhoto(generic.CreateView):
    model = Photo
    template_name = 'order_info.html'

    def post(self, request, pk):
        order = Order.objects.get(pk=pk)
        photo_form = PhotoForm(request.POST, request.FILES)
        if photo_form.is_valid():
            photo = photo_form.save(commit=False)
            photo.photographer = self.request.user
            for response in order.response_set.all():  # перебираем респонсы что бы вытащить тот где is_selected = True
                if response.is_selected == True:
                    photo.response = response
            photo.save()
            return redirect(reverse('photo_store:order', kwargs={'pk': order.id}))


class SelectResponseView(generic.UpdateView):
    """аналог функции select_response"""
    model = Response
    # queryset = Response.objects.all()
    template_name = 'order_info.html'

    # def get(self, request, pk):
    #     return self.post(request, pk)

    def get(self, request, pk):
        response = Response.objects.get(pk=pk)
        order = response.order
        response.is_selected = True
        response.save()
        # response.photographer.permissions.add(can_execute_permission)
        can_execute = Permission.objects.get(codename='can_execute')
        response.photographer.user_permissions.add(can_execute)
        order_url = reverse('photo_store:order', kwargs={'pk': order.id})
        Message.objects.create(text=f'Вас выбрали исполнителем заказа <a href="{order_url}">{order}</a>',
                               sender=order.owner,
                               receiver=response.photographer)
        send_mail(
            'Photo_Store: информация по заказу ' + str(order),
            'Поздровляем, вас выбрали исполнителем!',
            'admin@photo_store.ru',
            [response.photographer.email]
        )
        # del_response = Response.objects.filter(order=order)
        # for s in del_response:
        #     if not s.is_selected:
        #         s.delete()
        return redirect(reverse('photo_store:order', kwargs={'pk': order.id}))

# def select_response(request, response_id):
#     """функция выбора отклика"""
#     response = Response.objects.get(pk=response_id)
#     order = response.order
#     order_url = '/order/' + str(order.id) + '/'  # 'url "photo_store:order" order_id=order.id'
#     response.is_selected = True
#     response.save()
#     Message.objects.create(text=f'Вас выбрали исполнителем заказа <a href="{order_url}">{order}</a>',
#                            sender=order.owner,
#                            receiver=response.photographer)
#     del_response = Response.objects.filter(order=order)
#     for s in del_response:
#         if not s.is_selected:
#             s.delete()
#     return redirect(reverse('photo_store:order', kwargs={'order_id': order.id}))


class EditOrderUpdateView(generic.UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'edit_order.html'

    def get_success_url(self):
        return reverse('photo_store:profile')


# def edit_order(request, order_id):
#     """редактирование заказа"""
#     order = Order.objects.get(id=order_id)
#     if request.method == 'POST':
#         form = OrderForm(request.POST, instance=order)
#         if form.is_valid():
#             form.save()
#             # order.text = form.cleaned_data['text']
#             # order.price = form.cleaned_data['price']
#             # order.save()
#             return redirect(reverse('photo_store:order', kwargs={'order_id': order.id}))
#     else:
#         form = OrderForm(initial=model_to_dict(order))
#     return render(request, 'edit_order.html', {
#         'order_form': form
#     })


class DeleteOrderView(generic.DeleteView):
    model = Order
    template_name = 'order_info.html'

    def get_success_url(self):
        return reverse('photo_store:show_profile', kwargs={'pk': self.request.user.id})

    def get(self, request, pk):
        return self.post(request, pk)


# def del_order(request, order_id):
#     """удалить заказ"""
#     order = Order.objects.get(id=order_id)
#     if not order.response_set.filter(is_selected=True).first():  # если у заказа выбран исполнитель заказ удалить нельзя
#         order.delete()
#         return redirect(reverse('photo_store:orders'))
#     else:
#         return redirect(reverse('photo_store:orders'))


class OkView(generic.TemplateView):
    template_name = 'ok.html'


# def add_response(request, order_id):
#     if request.method == 'POST':
#         text = request.POST['text']
#         is_selected = True if 'is_selected' in request.POST else False
#         rate = request.POST['rate']
#         order = Order.objects.get(id=order_id)
#         Response.objects.create(text=text,
#                                 is_selected=is_selected,
#                                 rate=rate,
#                                 photographer=request.user,
#                                 order=order)
#     return redirect('/ok/')


class PhotoDetailView(generic.DetailView):
    model = Photo
    template_name = 'photo_view.html'

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'] = TagForm()
        return context


class TagCreateView(generic.CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'photo_view.html'

    def post(self, request, photo_id):
        form = self.form_class(request.POST)
        if form.is_valid():
            tag = form.save()
            tag.photo_set.add(Photo.objects.get(pk=photo_id))
        return redirect(reverse('photo_store:photo_view', kwargs={'pk': photo_id}))


# def photo_view(request, photo_id):
#     """функия просмотра отдельной фотографии"""
#     photo = Photo.objects.only('image', 'description', 'tags').get(id=photo_id)
#     if request.method == 'POST':
#         form = TagForm(request.POST)
#         if form.is_valid():
#             tag, created = Tag.objects.get_or_create(name=form.cleaned_data['name'])
#             photo.tags.add(tag)
#     form = TagForm()
#     return render(request, 'photo_view.html', {
#         'current_photo': photo,
#         'form': form
#     })


class TagPhotoDetailView(generic.DetailView):
    model = Tag
    template_name = 'tag_photos.html'
    context_object_name = 'tag'


# def tag_photos(request, tag_id):
#     """тэги фотографии"""
#     tag = Tag.objects.get(id=tag_id)
#     return render(request, 'tag_photos.html', {
#         'tag': tag
#     })


class RegistrationFormView(generic.FormView):
    template_name = 'register.html'
    form_class = RegistrationUserForm


class UserCreateView(generic.CreateView):
    model = User

    def post(self, request, *args, **kwargs):
        form = RegistrationUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['password_1'] == form.cleaned_data['password_2']:
                user.set_password(form.cleaned_data['password_1'])
                user.save()
                if form.cleaned_data['is_photographer'] == True:
                    photographer_group = Group.objects.get(name='Photographers')
                    user.groups.add(photographer_group)
                else:
                    client_group = Group.objects.get(name='Client')
                    user.groups.add(client_group)
                login_user = authenticate(request, username=user.username, password=form.cleaned_data['password_1'])
                login(request, login_user)
                print(user.email)
                send_mail(
                    'Photo_Store: Добро пожаловать!',
                    'Какой ты молодец!',
                    'admin@photo_store.ru',
                    [user.email]
                          )
                return redirect(reverse('photo_store:show_profile', kwargs={'pk': request.user.id}))
        else:
            return redirect('register/')


# def registration(request):
#     """регистрация"""
#     if request.method == 'POST':
#         form = RegistrationUserForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             if form.cleaned_data['password_1'] == form.cleaned_data['password_2']:
#                 user.set_password(form.cleaned_data['password_1'])
#                 user.save()
#                 login_user = authenticate(request, username=user.username, password=form.cleaned_data['password_1'])
#                 login(request, login_user)
#                 return redirect(reverse('photo_store:show_profile', kwargs={'user_id': request.user.id}))
#     else:
#         form = RegistrationUserForm()
#     return render(request, 'register.html', {
#         'form': form
#     })


"""Тестовые функции для DRF"""


def test_ajax(request):
    order = Order.objects.first()
    # print(model_to_dict(order))
    # response = json.dumps(model_to_dict(order), cls=DjangoJSONEncoder)
    serializer = OrderSerializer(order)
    print(type(serializer.data))
    print(serializer.data)
    return HttpResponse(json.dumps(serializer.data))


def create_ajax(request):
    # if request.is_ajax():
    # order_data = json.loads(request.body)
    # print(order_data, type(order_data))
    serializer = OrderSerializer(data=json.loads(request.body))
    if serializer.is_valid():
        serializer.save(owner=request.user)
        # Order.objects.create(
        #     text=serializer.validated_data['text'],
        #     price=serializer.validated_data['price'],
        #     start_date=serializer.validated_data['start_date'],
        #     finish_date=serializer.validated_data['finish_date'],
        #     date_time=datetime.datetime.now(),
        #     owner=request.user,
        #     topic=Topic.objects.get(pk=1)
        # )
    else:
        print(serializer.errors)
    return HttpResponse('ok')


def create_response_ajax(request, order_id):
    serializer = ResponseSerializer(data=json.loads(request.body))
    # print(serializer)
    if serializer.is_valid():
        serializer.save(photographer=request.user, order=Order.objects.get(pk=order_id))
        # Response.objects.create(
        #     text=serializer.validated_data['text'],
        #     # date_time=datetime.datetime.now(),
        #     is_selected=False,
        #     photographer=request.user,
        #     order=Order.objects.get(pk=45)
        # )
    else:
        print(serializer.errors)
    return HttpResponse('ok')


def create_message_ajax(request, pk):
    serializer = MessageSerializer(data=json.loads(request.body))
    if serializer.is_valid():
        serializer.save(sender=request.user, receiver=User.objects.get(pk=pk))
    else:
        print(serializer.errors)
    return HttpResponse(json.dumps(serializer.data))


@api_view(['GET'])
def show_message_ajax(request, pk):
    message = Message.objects.get(pk=pk)
    serialiazer = ShowMessageSerializer(message)
    return Response(serialiazer.data)


@api_view(['GET'])
def show_order_ajax(request, pk):
    order = Order.objects.get(pk=pk)
    serializer = ExtendOrderSerializer(order)
    return Response(serializer.data)


@api_view(['POST'])
def create_order_api(request):
    if request.method == 'POST':
        serializer = ExtendOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
