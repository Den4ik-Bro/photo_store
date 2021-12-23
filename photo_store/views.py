import datetime
from itertools import chain
import django_filters
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User, Group
from .models import Photo, Message, Order, Topic, Response, Tag
from django.db.models import Q, Prefetch, Avg, Count
from .forms import ProfileForm, OrderForm, ResponseForm, PhotoForm, SendMessageForm, RegistrationUserForm, TagForm, \
    RateResponseForm, InviteForm, EditProfileImageForm
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model, authenticate, login
from django.forms import modelformset_factory, formset_factory
from django.views import generic
from django.core.mail import send_mail
from .serializers import ResponseSerializer, MessageSerializer, ShowMessageSerializer, \
    ExtendOrderSerializer, MessageCreateSerializer, PhotoSerializer, UserSerializer, TopicSerializer, \
    UserPhotoSerializer, UserResponsePhotoSerializer
import json
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.decorators import api_view, action
from rest_framework.response import Response as RestResponse
from rest_framework.views import APIView
from rest_framework import status, filters
from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly, IsOwner

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


class DeletePhotoView(generic.DeleteView):
    model = Photo

    def get_success_url(self):
        return reverse('photo_store:show_profile', kwargs={'pk': self.request.user.id})

    def get(self, request, pk):
        return self.post(request, pk)


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


class EditProfileImageView(generic.UpdateView):
    model = User
    form_class = EditProfileImageForm
    template_name = 'edit_profile_image.html'

    def post(self, request, *args, **kwargs):
        form = EditProfileImageForm(request.POST, request.FILES)
        user = self.get_object()
        if form.is_valid():
            user.profile_image = request.FILES['profile_image']
            user.save()
            return redirect(reverse('photo_store:show_profile', kwargs={'pk': request.user.id}))
        return redirect(reverse('photo_store:show_profile', kwargs={'pk': request.user.id}))



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
            Message.objects.create(text=f'На ваш заказ {order} откликнулся {response.photographer}',   # сообщение заказчику от исполнителя
                                   sender=response.photographer,
                                   receiver=order.owner)
            # временно отключил отправку почты
            # send_mail(
            #     'Photo_Store: информация по заказу ' + str(order),
            #     'На ваш заказ откликнулся ' + str(response.photographer),
            #     'admin@photo_store.ru',
            #     [order.owner.email]
            # )
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


class EditOrderUpdateView(generic.UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'edit_order.html'

    def get_success_url(self):
        return reverse('photo_store:profile')


class DeleteOrderView(generic.DeleteView):
    model = Order
    template_name = 'order_info.html'

    def get_success_url(self):
        return reverse('photo_store:show_profile', kwargs={'pk': self.request.user.id})

    def get(self, request, pk):
        return self.post(request, pk)


class OkView(generic.TemplateView):
    template_name = 'ok.html'


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
        photo = Photo.objects.get(pk=photo_id)
        if form.is_valid():
            # tag = form.save()
            tag, created = Tag.objects.get_or_create(name=form.cleaned_data['name'])
            tag.photo_set.add(photo)
        return redirect(reverse('photo_store:photo_view', kwargs={'pk': photo_id}))


class TagPhotoDetailView(generic.DetailView):
    model = Tag
    template_name = 'tag_photos.html'
    context_object_name = 'tag'


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


"""Функции и классы DRF"""


def test_ajax(request):
    order = Order.objects.first()
    # print(model_to_dict(order))
    # response = json.dumps(model_to_dict(order), cls=DjangoJSONEncoder)
    serializer = ExtendOrderSerializer(order)
    print(type(serializer.data))
    print(serializer.data)
    return HttpResponse(json.dumps(serializer.data))


def create_ajax(request):
    # if request.is_ajax():
    # order_data = json.loads(request.body)
    # print(order_data, type(order_data))
    serializer = ExtendOrderSerializer(data=json.loads(request.body))
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
    return RestResponse(serialiazer.data)


@api_view(['POST'])
def create_message_api(request):
    if request.method == 'POST':
        serializer = MessageCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return RestResponse(serializer.data)
        else:
            return RestResponse(serializer.errors)


@api_view(['GET'])
def show_order_ajax(request, pk):
    order = Order.objects.get(pk=pk)
    serializer = ExtendOrderSerializer(order)
    return RestResponse(serializer.data)


@api_view(['GET'])
def show_order_ist_api(request):
    order = Order.objects.all()
    serializer = ExtendOrderSerializer(order, many=True)
    return RestResponse(serializer.data)


@api_view(['POST', 'PUT'])
def create_or_update_order_api(request, pk=None):
    if request.method == 'POST' or request.method == 'PUT':
        if pk:
            order = Order.objects.get(pk=pk)
            serializer = ExtendOrderSerializer(data=request.data, instance=order)
        else:
            serializer = ExtendOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return RestResponse(serializer.data)
        else:
            return RestResponse(serializer.errors)


@api_view(['GET'])
def show_photo_ajax(request, pk):
    photo = Photo.objects.get(pk=pk)
    serializer = PhotoSerializer(photo)
    return RestResponse(serializer.data)


@api_view(['POST'])
def create_photo_api(request, pk):
    if request.method == 'POST':
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return RestResponse(serializer.data)
        return RestResponse(serializer.errors)



#
#
# class ApiOrderDetailView(APIView):
#
#     def get_object(self, pk):
#         try:
#             order = Order.objects.get(pk=pk)
#         except Order.DoesNotExist:
#             raise Http404
#         return order
#
#     def get(self, request, pk):
#         order = self.get_object(pk)
#         serializer = ExtendOrderSerializer(order)
#         return RestResponse(serializer.data)
#
#     def put(self, request, pk):
#         order = self.get_object(pk)
#         serializer = ExtendOrderSerializer(order, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return RestResponse(serializer.data)
#         return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         order = self.get_object(pk)
#         order.delete()
#         return RestResponse(status=status.HTTP_204_NO_CONTENT)


# class ApiListUpdateOrderView(mixins.ListModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
#     queryset = Order.objects.all()
#     serializer_class = ExtendOrderSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
#
#     def put(self, request, pk, *args, **kwargs):
#         return self.update(request, pk, *args, **kwargs)


# class ApiListUpdateOrderView(generics.RetrieveUpdateDestroyAPIView):
#     pass


# class OrderViewSet(viewsets.ViewSet):
#
#     def list(self, request):
#         orders = Order.objects.all()
#         serializer = ExtendOrderSerializer(orders, many=True)
#         return RestResponse(serializer.data)
#
#     def retrieve(self, request, pk):
#         order = Order.objects.get(pk=pk)
#         serializer = ExtendOrderSerializer(order)
#         return RestResponse(serializer.data)
#
#     def destroy(self, request, pk):
#         Order.objects.get(pk=pk).delete()
#         return RestResponse(status=status.HTTP_204_NO_CONTENT)
#
#     def update(self, request, pk):
#         order = Order.objects.get(pk=pk)
#         serializer = ExtendOrderSerializer(data=request.data, instance=order)
#         if serializer.is_valid():
#             serializer.save()
#             return RestResponse(serializer.data, status=status.HTTP_200_OK)
#         return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def partial_update(self, request, pk):
#         order = Order.objects.get(pk=pk)
#         serializer = ExtendOrderSerializer(data=request.data, instance=order, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return RestResponse(serializer.data, status=status.HTTP_200_OK)
#         return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def create(self, request):
#         serializer = ExtendOrderSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return RestResponse(serializer.data, status=status.HTTP_201_CREATED)
#         return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# order_list_view = OrderViewSet.as_view({'GET': 'list'})
# order_detail_view = OrderViewSet.as_view({'GET':'retrieve'})


class OrderApiViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = ExtendOrderSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['topic__name',]
    permission_classes = [IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return RestResponse(serializer.data)
        return RestResponse(serializer.errors)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username', 'email']

    @action(methods=['GET'], detail=True)
    def send_message_this_user(self, request, pk):
        user = User.objects.get(pk=pk)
        Message.objects.create(sender=request.user, receiver=user, text=request.data['text'])
        return RestResponse({'status':'the message has been sent'})


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = ShowMessageSerializer


class ResponseViewSet(viewsets.ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAdminUser, IsOwner]

    @action(detail=True, methods=['GET'])
    def select_for_order(self, request, pk):
        # if request.user.has_perm()
        response = self.get_object()
        if response.order.response_set.filter(is_selected=True).exists():
            return RestResponse({'status': 'for this order response already selected'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user != response.order.owner:
            return RestResponse({'status':'вы не можете выбрать отклик к этому заказу'}, status=status.HTTP_400_BAD_REQUEST)
        response.is_selected = True
        response.save()
        return RestResponse({'status': 'response selected'})


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAdminOrReadOnly]


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer


class UserPhotoApiViewSet(viewsets.ModelViewSet):
    """Портфолио пользователя"""
    serializer_class = UserPhotoSerializer

    def get_queryset(self):
        return self.request.user.photo_set.filter(response=None)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(photographer=request.user)
            return RestResponse(serializer.data, status=status.HTTP_201_CREATED)
        return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserResponsePhotoApiViewSet(viewsets.ModelViewSet):
    """Все фотографии пользователя к заказам"""
    serializer_class = UserResponsePhotoSerializer

    def get_queryset(self):
        return self.request.user.photo_set.filter(response__isnull=False)
        # user = self.request.user
        # return user.photo_set.filter(response__photographer=user)


class UserOrderApiViewSet(viewsets.ModelViewSet):
    """Все заказы псозданные ползователем"""
    serializer_class = ExtendOrderSerializer

    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = ExtendOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return RestResponse(serializer.data, status=status.HTTP_201_CREATED)
        return RestResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserResponseApiViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet
                             ):
    """Отклики пользователя"""
    serializer_class = ResponseSerializer

    def get_queryset(self):
        return Response.objects.filter(photographer=self.request.user)

    # @action(detail=True, methods=['GET'])
    # def is_selected(self):
    #     response = Response.objects.filter(photographer=self.request.user, is_selected=True)
    #     serializer = ResponseSerializer(response, many=True)
    #     return RestResponse(serializer.data)


class UserMessagesApiViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.CreateModelMixin,
                             viewsets.GenericViewSet
                             ):
    """Сообщения пользователя, где он либо отправитель, либо получатель"""
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user))

    @action(methods=['GET'], detail=True)
    def send_message(self, request, pk):
        message = self.get_object()
        if message.sender == request.user:
            receiver = message.receiver
        else:
            receiver = message.sender
        Message.objects.create(sender=request.user, receiver=receiver, text=request.data['text'])
        return RestResponse({'status': 'message created'})


