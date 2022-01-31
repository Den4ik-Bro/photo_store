from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class EditProfileImageForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('profile_image',)


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
            ]