from django.contrib.auth import get_user_model, authenticate, login
from django.core.mail import send_mail
from django.db.models import Prefetch, Avg
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic

from order.forms import InviteForm
from order.models import Order, Response
from message.forms import SendMessageForm
from message.models import Message
from photo_store.forms import PhotoForm

# from ..order.forms import InviteForm
# from ..order.models import Order, Response
#
# from ..message.forms import SendMessageForm
# from ..message.models import Message
#
# from ..photo_store.forms import PhotoForm

from .forms import ProfileForm, EditProfileImageForm, RegistrationUserForm

User = get_user_model()


def profile_login(request):
    """редирект на profile/<int:user_id>/"""
    return redirect(reverse('customer:show_profile', kwargs={'pk': request.user.id}))


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


class EditProfileView(generic.UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'edit_profile.html'

    def get_success_url(self):
        return reverse('customer:show_profile', kwargs={'pk': self.request.user.id})

    def get(self, request, pk):
        if pk != request.user.id:
            return redirect(reverse('customer:show_profile', kwargs={'pk': request.user.id}))
        return super().get(request, pk)

    def post(self, request, pk):
        if pk != request.user.id:
            return redirect(reverse('customer:show_profile', kwargs={'pk': request.user.id}))
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
            return redirect(reverse('customer:show_profile', kwargs={'pk': request.user.id}))
        return redirect(reverse('customer:show_profile', kwargs={'pk': request.user.id}))


class PhotographersListView(generic.ListView):
    model = User
    context_object_name = 'user'
    template_name = 'photographers.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        InviteFormSet = modelformset_factory(User, InviteForm, extra=0)
        context['form_set'] = InviteFormSet(queryset=User.objects.all()
                                 .exclude(pk=self.request.user.id)
                                 .annotate(avg_rate=Avg('response__rate')), form_kwargs={'owner': self.request.user})
        return context


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
                # if form.cleaned_data['is_photographer'] == True:
                #     photographer_group = Group.objects.get(name='Photographers')
                #     user.groups.add(photographer_group)
                # else:
                #     client_group = Group.objects.get(name='Client')
                #     user.groups.add(client_group)
                login_user = authenticate(request, username=user.username, password=form.cleaned_data['password_1'])
                login(request, login_user)
                print(user.email)
                send_mail(
                    'Photo_Store: Добро пожаловать!',
                    'Какой ты молодец!',
                    'admin@photo_store.ru',
                    [user.email]
                          )
                return redirect(reverse('customer:show_profile', kwargs={'pk': request.user.id}))
        else:
            return redirect('register/')