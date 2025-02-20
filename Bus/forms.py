from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import formset_factory
from  django.utils import timezone
from .models import *


class SearchForm(forms.Form):
    from_city = forms.ModelChoiceField(
        queryset=BusStop.objects.all(),
        label="From"
    )
    to_city = forms.ModelChoiceField(
        queryset=BusStop.objects.all(),
        label="To"
    )
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
    seat_class = forms.ModelChoiceField(queryset=SeatClass.objects.none(), empty_label=None)

    class Meta:
        model = Booking
        fields = ['travel_date']

    def __init__(self, *args, **kwargs):
        bus = kwargs.pop('bus', None)
        super().__init__(*args, **kwargs)

        if bus:
            self.fields['seat_class'].queryset = SeatClass.objects.filter(
                busseatclass__bus=bus
            ).distinct()

    def clean(self):
        cleaned_data = super().clean()
        travel_date = cleaned_data.get('travel_date')
        tickets = self.data.getlist('tickets')

        if not self.bus.is_operating_on_date(travel_date):
            raise forms.ValidationError("The selected bus does not operate on this date.")

        if self.bus.seat_classes.get_available_seats(travel_date) < len(tickets):
            raise forms.ValidationError("Not enough seats available.")

        if self.user.profile.wallet_balance < (self.bus.seat_classes.fare * len(tickets)):
            raise forms.ValidationError("Insufficient wallet balance.")

        return cleaned_data

class PassengerForm(forms.Form):
    name = forms.CharField(max_length=100)
    age = forms.IntegerField(min_value=1, max_value=100)

PassengerFormSet = formset_factory(
    PassengerForm,
    extra=1,
    min_num=1,
    validate_min=True
)

class RouteAdminForm(forms.ModelForm):
    # The 'buses' field is not actually on the Route model, but we add it for convenience.
    buses = forms.ModelMultipleChoiceField(
        queryset=Bus.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("Buses", is_stacked=False)
    )

    class Meta:
        model = Route
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['buses'].initial = self.instance.bus_set.all()

    def save(self, commit=True):
        route = super().save(commit=commit)
        if commit:
            self.instance.buses.update(route=None)
            for bus in self.cleaned_data['buses']:
                bus.route = route
                bus.save()
        return route