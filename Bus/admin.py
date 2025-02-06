from django.contrib import admin
from .models import *
from django.utils import timezone


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'wallet_balance', 'user_type')
    list_filter = ('user_type',)


class Bus(admin.ModelAdmin):
    filter_horizontal = 'scheduled_days'
    actions = ['cancel_bus']

    def cancel_bus(self, request, queryset):
        for bus in queryset:
            bookings = bus.bookings.filter(
                travel_date__gte=timezone.now().date(),
                status=bus.BookingStatus.ACCEPTED
            )
            for booking in bookings:
                booking.cancel()
            bus.is_active = False
            bus.save()