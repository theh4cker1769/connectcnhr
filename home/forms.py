from pyexpat import model
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User


class MyUserCreationForm(UserCreationForm):
    class Meta():
        model = User
        fields = ['name','username', 'email', 'password1', 'password2']


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['topic', 'name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control'})
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        ## fields = ['username', 'email']
        fields = ['avatar', 'name', 'username', 'email', 'bio']
