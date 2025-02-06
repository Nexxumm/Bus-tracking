from django.db import transaction
from django.utils import timezone
from django.views.generic import ListView, CreateView
from .models import *
from .forms import *


class BusSearchView(ListView):
    model = Bus
    template_name = 'booking/search_results.html'
    context_object_name = 'buses'

    def get_queryset(self):
        form = SearchForm(self.request.GET)
        if form.is_valid():
            return Bus.objects.filter(
                departure_point=form.cleaned_data['from_city'],
                destination=form.cleaned_data['to_city'],
                operating_days__number=form.cleaned_data['date'].weekday(),
                is_active=True
            ).exclude(departure_time__lt=timezone.now().time())
        return Bus.objects.none()


class BookingCreateView(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'booking/create_booking.html'

    def form_valid(self, form):
        bus = Bus.objects.get(pk=self.kwargs['bus_id'])
        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.bus = bus

        try:
            with transaction.atomic():
                booking.save()
                self.request.user.wallet_balance -= booking.total_cost
                self.request.user.save()
                return redirect('booking_confirmation', pk=booking.pk)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)