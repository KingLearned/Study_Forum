from django.forms import ModelForm
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User
from django.core.exceptions import ValidationError

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.pop('autofocus', None)

    def clean_password2(self):
        password2 = self.cleaned_data.get('password2')

        common_passwords = ["password", "12345678", "qwerty", "admin", "letmein", "welcome", "123abc"]

        if len(password2) < 6:
            raise ValidationError('This password is too short. It must contain at least 6 characters.')

        if password2.lower() in common_passwords:
            raise ValidationError('This password is too common.')

        if password2.isdigit():
            raise ValidationError('This password is entirely numeric.')

        return password2

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'bio']