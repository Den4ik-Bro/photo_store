from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Photo, Message, Order, Topic, Response, Tag
from django.db.models import Q, Prefetch
from .forms import ProfileForm, OrderForm, ResponseForm, PhotoForm, SendMessageForm, RegistrationUserForm, TagForm
from django.forms.models import model_to_dict


def main(request):
    """Главная страница"""
    users = User.objects.all()
    return render(request, 'main.html', {'users': users})


def profile_login(request):
    """редирект на profile/<int:user_id>/"""
    return redirect('/profile/' + str(request.user.id) + '/')


def profile(request, user_id):
    """функция профиля"""
    user = User.objects.prefetch_related\
        (
            Prefetch('order_set', Order.objects.select_related('topic', 'owner').all())
        )\
        .prefetch_related\
        (
            Prefetch('response_set', Response.objects.select_related('photographer').all())
        )\
        .prefetch_related\
        (
            Prefetch('message_set', Message.objects.select_related('sender', 'receiver').all())
        )\
        .get(pk=user_id)
    if request.method == 'POST':
        message_form = SendMessageForm(request.POST)
        photo_form = PhotoForm(request.POST, request.FILES)
        if photo_form.is_valid():
            photo = photo_form.save(commit=False)
            photo.photographer = request.user
            photo.save()
            return redirect('/profile/' + str(user.id) + '/')
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.sender = request.user
            message.receiver = User.objects.get(id=user_id)
            message.save()
            return redirect('/profile/' + str(user.id) + '/')
    photo_form = PhotoForm()
    message_form = SendMessageForm()
    return render(request, 'profile.html', {'user': user,
                                            'photo_form': photo_form,
                                             'message_form': message_form})


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


def edit_profile(request, user_id):
    """редактирование профиля"""
    form = ProfileForm()
    if request.method == 'POST':
        user = request.user
        # user.first_name = request.POST['first_name']
        # user.last_name = request.POST['last_name']
        # user.email = request.POST['email']
        form = ProfileForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['firstname']
            user.last_name = form.cleaned_data['lastname']
            user.email = form.cleaned_data['email']
            user.save()
            return redirect('/profile/' + str(user.id) + '/')
    return render(request, 'edit_profile.html', {'profile_form': form})


# def add_photo(request):
#     if request.method == 'POST':
#         form = PhotoForm(request.POST)
#         user = request.user
#         if form.is_valid():
#             photo = form.save(commit=False)
#             photo.photographer = user
#             photo.save()
#             return redirect('/profile/')
#     form = PhotoForm()
#     return redirect('/profile/')


def del_photo(request, photo_id):
    """Функция удаления фотографии. Комментарий от Леонида"""
    # if request.method == 'POST':
    user = request.user
    photo = Photo.objects.get(id=photo_id)
    photo.delete()
    return redirect('/profile/' + str(user.id) + '/')


# def message(request):
#     user = request.user
#     messages = Message.objects.filter(Q(sender=user) | Q(receiver=user))
#     form = MessageForm()
#     if request.method == 'POST':
#         form = MessageForm(request.POST)
#         if form.is_valid():
#             message = form.save(commit=False)
#             message.sender = user
#             message.save()
#             return redirect('/profile/' + str(user.id) + 'message/')
#     return render(request, 'message.html', {'messages': messages,
#                                             'form': form})


def orders(request):
    """Заказы"""
    orders = Order.objects.only('topic', 'owner',).exclude(owner=request.user).all()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.owner = request.user
            order.save()
            return redirect('/profile/' + str(order.owner.id) + '/')
    form = OrderForm()
    return render(request, 'orders.html', {'user_orders': orders,
                                           'form': form})


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


def get_order(request, order_id):
    """просмотр заказа и добавление отклика на заказ"""
    order = Order.objects.only('topic', 'owner', 'price', 'text')\
                            .select_related('topic', 'owner')\
                            .prefetch_related\
                                (
                                    Prefetch('response_set', Response.objects.select_related('photographer').all())
                                )\
                            .get(id=order_id)
    # responses = Response.objects.filter(order=order)  # все объекты респонса по этому заказу
    is_user_has_response = order.response_set.filter(photographer=request.user).exists()
    accepted_response = order.response_set.filter(is_selected=True).first()
    if request.method == 'POST':  # добавить отклик
        form = ResponseForm(request.POST)
        photo_form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save(commit=False)
            response.order = order
            response.photographer = request.user
            response.is_selected = False
            response.save()
            return redirect('/ok/')
        if photo_form.is_valid():
            photo = photo_form.save(commit=False)
            photo.photographer = request.user
            photo.response = order.response_set.get(is_selected=True)
            photo.save()
    form = ResponseForm()
    photo_form = PhotoForm()
    context = {'current_order': order,
               'is_user_has_response': is_user_has_response,
               'accepted_response': accepted_response,
               'form': form,
               'photo_form': photo_form}
    if accepted_response:
        photos = Photo.objects.filter(response=accepted_response)
        context['photo'] = photos
    return render(request, 'order_info.html', context)


def select_response(request, response_id):
    """функция выбора отклика"""
    response = Response.objects.get(id=response_id)
    order = response.order
    response.is_selected = True
    response.save()
    return redirect('/order/' + str(order.id) + '/')


def edit_order(request, order_id):
    """редактирование заказа"""
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            # order.text = form.cleaned_data['text']
            # order.price = form.cleaned_data['price']
            # order.save()
            return redirect('/order/' + str(order.id) + '/')
    else:
        form = OrderForm(initial=model_to_dict(order))
    return render(request, 'edit_order.html', {'order_form': form})


def del_order(request, order_id):
    """удалить заказ"""
    order = Order.objects.get(id=order_id)
    order.delete()
    return redirect('/orders/')


def ok(request):
    """отклик добавлен успешно"""
    return render(request, 'ok.html')


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


def photo_view(request, photo_id):
    """функия просмотра отдельной фотографии"""
    photo = Photo.objects.only('image', 'description', 'tags').get(id=photo_id)
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag, created = Tag.objects.get_or_create(name=form.cleaned_data['name'])
            photo.tags.add(tag)
    form = TagForm()
    return render(request, 'photo_view.html', {'current_photo': photo,
                                               'form': form})


def tag_photos(request, tag_id):
    """тэги фотографии"""
    tag = Tag.objects.get(id=tag_id)
    return render(request, 'tag_photos.html', {'tag': tag})


def registration(request):
    """регистрация"""
    if request.method == 'POST':
        form = RegistrationUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['password_1'] == form.cleaned_data['password_2']:
                user.set_password(form.cleaned_data['password_1'])
                user.save()
                return redirect('/login/')
    else:
        form = RegistrationUserForm()
    return render(request, 'register.html', {'form': form})


