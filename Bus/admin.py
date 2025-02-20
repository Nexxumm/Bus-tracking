from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
import nested_admin
from .models import *
from .forms import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'wallet_balance', 'user_type')
    list_filter = ('user_type',)

class BusScheduledDayInline(admin.TabularInline):
    model = BusSchedule
    extra = 1


class BusSeatClassInline(admin.TabularInline):
    model = BusSeatClass
    extra = 1

class RouteStopInline(nested_admin.NestedTabularInline):
    model = RouteStop
    extra = 1

@admin.register(Route)
class RouteAdmin(nested_admin.NestedModelAdmin):
    form = RouteAdminForm
    list_display = ('name', 'fare')
    inlines = [RouteStopInline]


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('number', 'departure', 'destination', 'departure_time', 'arrival_time', 'is_active','fare', 'get_scheduled_days')
    list_filter = ('is_active', 'departure', 'destination')
    search_fields = ('number', 'departure', 'destination')
    inlines = [BusScheduledDayInline, BusSeatClassInline]

    def view_bookings(self, request, queryset):
        selected = queryset.first()
        if selected:
            return HttpResponseRedirect(reverse('admin:Bus_booking_changelist') + f'?bus__id__exact={selected.id}')

    view_bookings.short_description = "View bookings for selected bus"

    @transaction.atomic
    def cancel_bus_and_refund(self, request, queryset):
        for bus in queryset:
            bookings = Booking.objects.filter(bus=bus, status='ACCEPTED')
            for booking in bookings:
                booking.cancel()
            bus.is_active = False
            bus.save()

    cancel_bus_and_refund.short_description = "Cancel bus and refund tickets"
    actions = ['view_bookings', 'cancel_bus_and_refund']
'''    def export_reservations(self, request, queryset):
        if len(queryset) != 1:
            self.message_user(request, "Please select only one bus to export reservations.")
            return

        bus = queryset[0]
        bookings = Booking.objects.filter(bus=bus)
        resource = BookingResource()
        dataset = resource.export(bookings)
        response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="reservations_bus_{bus.number}.xls"'
        return response

    export_reservations.short_description = "Export reservations to Excel"
'''





@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('bus', 'user', 'seat_class', 'travel_date', 'status')
    list_filter = ('bus', 'status', 'travel_date')
    search_fields = ('user', 'bus__number')

@admin.register(BusStop)
class BusStopAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'code')
    search_fields = ('name', 'city', 'code')


