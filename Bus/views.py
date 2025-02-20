from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import OuterRef, Subquery, IntegerField, F
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
            from_stop = form.cleaned_data['from_city']
            to_stop = form.cleaned_data['to_city']
            search_date = form.cleaned_data['date']
            weekday = search_date.weekday()

            # Subquery to find the stop order for the departure stop on a route
            departure_order_subquery = RouteStop.objects.filter(
                route=OuterRef('route'),
                stop=from_stop
            ).order_by('order').values('order')[:1]

            # Subquery to find the stop order for the destination stop on a route
            destination_order_subquery = RouteStop.objects.filter(
                route=OuterRef('route'),
                stop=to_stop
            ).order_by('order').values('order')[:1]

            qs = Bus.objects.filter(
                is_active=True,
                scheduled_days__number=weekday,
            ).annotate(
                departure_order=Subquery(departure_order_subquery, output_field=IntegerField()),
                destination_order=Subquery(destination_order_subquery, output_field=IntegerField()),
            ).filter(
                departure_order__isnull=False,
                destination_order__isnull=False,
                departure_order__lt=F('destination_order')
            )

            # Only filter out buses with departure times in the past if the search date is today
            if search_date == timezone.localdate():
                qs = qs.exclude(departure_time__lt=timezone.now().time())

            return qs.distinct()

        return Bus.objects.none()


    def get_context_data(self, **kwargs):                         #passes form to template
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm(self.request.GET)
        return context


class BookingCreateView(CreateView):
    model = Booking
    fields = []
    template_name = 'Bus/create_booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Only add formset if not already in context (e.g., when re-rendering after invalid form)
        if 'formset' not in context:
            context['formset'] = PassengerFormSet(initial=[{}])
        context['seat_class_id'] = self.kwargs.get('seat_class_id')
        context['start_stop'] = self.request.GET.get('start_stop')
        context['end_stop'] = self.request.GET.get('end_stop')
        context['travel_date'] = self.request.GET.get('travel_date')
        return context

    def post(self, request, *args, **kwargs):
        formset = PassengerFormSet(request.POST)
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    def form_valid(self, formset):
        bus = get_object_or_404(Bus, pk=self.kwargs['bus_id'])
        seat_class = get_object_or_404(SeatClass, pk=self.kwargs['seat_class_id'])
        start_stop_id =  self.request.GET.get('start_stop')
        end_stop_id =  self.request.GET.get('end_stop')
        travel_date =  self.request.GET.get('travel_date')

        if not (start_stop_id and end_stop_id and travel_date):


            messages.error(self.request, 'Please enter both start &  stop ')
            return self.form_invalid(formset)

        try:
            travel_date_obj = datetime.strptime(travel_date.strip(), "%Y-%m-%d").date()
        except ValueError:
            messages.error(self.request, "Invalid date format")
            return redirect('search_results')

        start_stop = get_object_or_404(BusStop, pk=start_stop_id)
        end_stop = get_object_or_404(BusStop, pk=end_stop_id)

        passengers_data = []
        for form in formset:
            if form.cleaned_data:
                passengers_data.append({
                    'name': form.cleaned_data['name'],
                    'age': form.cleaned_data['age']
                })

            total_cost = bus.fare * seat_class.fare_multiplier * len(passengers_data)

        try:
            booking = create_booking(
                user=self.request.user,
                bus=bus,
                seat_class=seat_class,
                passengers_data=passengers_data,
                travel_date=travel_date_obj ,
                start_stop=start_stop,
                end_stop=end_stop,
                total_cost=total_cost,
                )

            self.object = booking
            messages.success(self.request, "Your booking was created successfully!")
            return redirect('profile')
        except ValueError as e:
            messages.error(self.request, f'error: {e}')
            return redirect('search_results')

    def form_invalid(self, formset):
        self.object = None
        context = self.get_context_data(formset=formset)                # form_invalid definition for a formset
        return self.render_to_response(context)


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

