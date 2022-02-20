from django import forms
from django.contrib.admin import widgets
from django.contrib.auth import get_user_model
from django.forms import SelectDateWidget

from .models import Order, Response

User = get_user_model()


class MyDateInput(forms.DateInput):
    input_type = 'date'
    format = '%Y-%m-%d'


class InviteForm(forms.ModelForm):
    orders = forms.ModelChoiceField(queryset=None, label='заказ', required=False)

    class Meta:
        model = User
        fields = ('id',)

    def __init__(self, owner, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['orders'].queryset = Order.objects.filter(owner=owner)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = \
            [
                'date_create',
                'owner',
            ]
        widgets = {'photo_date': SelectDateWidget(), }


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