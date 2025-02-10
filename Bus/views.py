from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, CreateView
from .models import *
from .forms import *
from .services import create_booking


class BusSearchView(ListView):
    model = Bus
    template_name = 'Bus/search_results.html'
    context_object_name = 'buses'

    def get_queryset(self):
        form = SearchForm(self.request.GET)
        if form.is_valid():
            return Bus.objects.filter(
                departure=form.cleaned_data['from_city'],
                destination=form.cleaned_data['to_city'],
                scheduled_days__number=form.cleaned_data['date'].weekday(),
                is_active=True
            ).exclude(departure_time__lt=timezone.now().time())
        return Bus.objects.none()

    def get_context_data(self, **kwargs):                         #passes form to template
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm(self.request.GET)
        return context


class BookingCreateView(CreateView):
    model = Booking
    fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = PassengerFormSet()
        return context

    def post(self, request, *args, **kwargs):
        formset = PassengerFormSet(request.POST)
        if formset.is_valid():
            return self.form_valid(formset)
        return self.form_invalid(formset)

    def form_valid(self, formset):
        bus = get_object_or_404(Bus, pk=self.kwargs['bus_id'])
        seat_class = get_object_or_404(SeatClass, pk=self.kwargs['seat_class_id'])

        passengers_data = [
            {'name': form.cleaned_data['name'], 'age': form.cleaned_data['age']}
            for form in formset
        ]

        try:
            booking = create_booking(
                user=self.request.user,
                bus=bus,
                seat_class=seat_class,
                passengers_data=passengers_data
            )
            return redirect('booking_confirmation', pk=booking.pk)
        except ValueError as e:
            formset.add_error(None, str(e))
            return self.form_invalid(formset)


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    if booking.status == Booking.status.ACCEPTED:
        if booking.can_be_cancelled():
            booking.cancel()
            messages.success(request, "Booking cancelled successfully. Amount refunded to your wallet.")
        else:
            messages.error(request, "Cancellation is only allowed up to 6 hours before departure.")
    else:
        messages.error(request, "This booking is already cancelled.")

    return redirect('profile')

