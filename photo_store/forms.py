from django import forms
from .models import Photo
from django.contrib.auth import get_user_model

User = get_user_model()

# class ProfileForm(forms.Form):
#     firstname = forms.CharField(label='Имя:', max_length=10)
#     lastname = forms.CharField(label='Фамилия', max_length=20)
#     email = forms.EmailField(required=False)


# class OrderForm(forms.Form):
#     text = forms.CharField(label='Текст заказа', widget=forms.Textarea)
#     price = forms.IntegerField(label='Цена')


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = \
            [
                'image',
                'description'
            ]


# class TagForm(forms.ModelForm):
#     class Meta:
#         model = Tag
#         fields = ['name']
#
#     def save(self, commit=True):
#         tag, created = Tag.objects.get_or_create(name=self.cleaned_data['name'])
#         return tag

    # def is_valid(self):
    #     self.cleaned_data = {'name':}
    #     return True


class TagForm(forms.Form):
    name = forms.CharField(label='Тэг', widget=forms.TextInput(attrs={
        'class': "form-control form-control-sm",
        'text': 'text',
        'placeholder': 'Добавте тэг',
        'aria-label': '.form-control-sm example',
    }))





