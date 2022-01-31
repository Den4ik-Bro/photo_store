from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        exclude =\
            [
                'date_time',
                'response',
                'sender'
            ]
        # widgets = {}


class SendMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']