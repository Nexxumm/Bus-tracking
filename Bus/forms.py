from django import forms
from  django.utils import timezone
from .models import *


class SearchForm(forms.Form):
    from_city = forms.CharField(label='From', max_length=100)
    to_city = forms.CharField(label='To', max_length=100)
    date = forms.DateField(label='Travel Date', widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.now().date():
            raise forms.ValidationError("Travel date cannot be in the past.")
        return date



class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['passenger_name', 'passenger_age']

class BookingForm(forms.ModelForm):
    tickets = forms.formset_factory(TicketForm, extra=1, min_num=1)

    class Meta:
        model = Booking
        fields = ['travel_date']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.bus = kwargs.pop('bus', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        travel_date = cleaned_data.get('travel_date')
        tickets = self.data.getlist('tickets')

        if not self.bus.is_operating_on_date(travel_date):
            raise forms.ValidationError("The selected bus does not operate on this date.")

        if self.bus.get_available_seats(travel_date) < len(tickets):
            raise forms.ValidationError("Not enough seats available.")

        if self.user.wallet_balance < (self.bus.base_fare * len(tickets)):
            raise forms.ValidationError("Insufficient wallet balance.")

        return cleaned_data

