from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, UpdateView
from Bus.models import *



class AdminDashboardView(UserPassesTestMixin, ListView):
    model = Bus
    template_name = 'admin/dashboard.html'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_bookings'] = Booking.objects.filter(
            travel_date__gte=timezone.now().date()
        )[:10]
        return context


class BusUpdateView(UserPassesTestMixin, UpdateView):
    model = Bus
    fields = ['total_seats', 'base_fare', 'departure_time', 'arrival_time', 'is_active']
    template_name = 'admin/bus_edit.html'

    def test_func(self):
        return self.request.user.is_admin

    def form_valid(self, form):
        if not form.instance.is_active:
            self.cancel_future_bookings(form.instance)
        return super().form_valid(form)

    def cancel_future_bookings(self, bus):
        future_bookings = bus.bookings.filter(
            travel_date__gte=timezone.now().date(),
            status=Booking.status.ACCEPTED,
        )
        for booking in future_bookings:
            booking.cancel()