from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator

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


class WalletTopupForm(forms.Form):
    amount = forms.IntegerField(
        label="Top-up Amount",
        validators=[MinValueValidator(1)],
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data['amount'] # clean amount
        return amount


