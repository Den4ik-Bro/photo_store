from django import forms
from .models import Order, Response, Photo, Message, Tag
from django.contrib.auth import get_user_model

User = get_user_model()

# class ProfileForm(forms.Form):
#     firstname = forms.CharField(label='Имя:', max_length=10)
#     lastname = forms.CharField(label='Фамилия', max_length=20)
#     email = forms.EmailField(required=False)


# class OrderForm(forms.Form):
#     text = forms.CharField(label='Текст заказа', widget=forms.Textarea)
#     price = forms.IntegerField(label='Цена')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        # fields = '__all__'
        # fields = ['topic', 'text', 'price', 'is_public']
        exclude = \
            [
                'date_time',
                'owner'
            ]


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']


class RateResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = \
            [
                'rate',
                'comment'
            ]


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = \
            [
                'image',
                'description'
            ]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        exclude =\
            [
                'date_time',
                'response',
                'sender'
            ]


class SendMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']


class RegistrationUserForm(forms.ModelForm):
    password_1 = forms.CharField(widget=forms.PasswordInput(), label='Введите пароль')
    password_2 = forms.CharField(widget=forms.PasswordInput(), label='Повторите пароль')

    class Meta:
        model = User
        fields = \
            [
                'username',
                'first_name',
                'last_name',
                'email',
                'is_photographer'
            ]


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']


class InviteForm(forms.ModelForm):
    orders = forms.ModelChoiceField(queryset=None, label='заказ')

    class Meta:
        model = User
        fields = ('id',)

    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['orders'].queryset=Order.objects.filter(owner=owner)


