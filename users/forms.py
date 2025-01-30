from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from Bus.models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email']

class AddToWalletForm(forms.ModelForm):
    wallet = forms.IntegerField()
    class Meta:
        model = Profile
        fields = ['wallet_balance']




