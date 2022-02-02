from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.mail import send_mail
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic

from .forms import InviteForm, OrderForm, ResponseForm, RateResponseForm
from .models import Order, Response

from message.models import Message
from photo_store.models import Photo
from photo_store.forms import PhotoForm

# from ..message.models import Message
# from ..photo_store.models import Photo
# from ..photo_store.forms import PhotoForm

User = get_user_model()


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
                    order_url = reverse('order:order', kwargs={'pk': order.id})
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
            return redirect(reverse('customer:show_profile', kwargs={'pk': self.request.user.id}))
        else:
            return redirect(reverse('customer:photographers'))


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
        context['order_form'] = OrderForm()
        return context


class OrderCreateView(generic.CreateView):
    model = Order

    def post(self, request, *args, **kwargs):
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.owner = request.user
            order.save()
            return redirect(reverse('customer:profile'))
        return redirect(reverse('order:orders'))


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
            Message.objects.create(text=f'На ваш заказ {order} откликнулся {response.photographer}',
                                   sender=response.photographer,
                                   receiver=order.owner)
            send_mail(
                'Photo_Store: информация по заказу ' + str(order),
                'На ваш заказ откликнулся ' + str(response.photographer),
                'admin@photo_store.ru',
                [order.owner.email]
            )
            return redirect(reverse('order:order', kwargs={'pk': order.id}))
        return redirect(reverse('order:order', kwargs={'pk': order.id}))


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
            return redirect(reverse('order:order', kwargs={'pk': order.id}))
        else:
            return redirect(reverse('order:order', kwargs={'pk': order.id}))


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
        del_response = Response.objects.filter(order=order)
        for s in del_response:
            if not s.is_selected:
                s.delete()
        return redirect(reverse('order:order', kwargs={'pk': order.id}))


class EditOrderUpdateView(generic.UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'edit_order.html'

    def get_success_url(self):
        order = self.get_object()
        return reverse('order:order', kwargs={'pk': order.id})


class DeleteOrderView(generic.DeleteView):
    model = Order
    template_name = 'order_info.html'

    def get_success_url(self):
        return reverse('customer:show_profile', kwargs={'pk': self.request.user.id})

    def get(self, request, pk):
        return self.post(request, pk)


class OkView(generic.TemplateView):
    template_name = 'ok.html'