from django.contrib import admin
from .models import *
from django.utils import timezone
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'wallet_balance', 'user_type')
    list_filter = ('user_type',)



@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('number', 'departure', 'destination', 'total_seats', 'fare')



@admin.register(BusStop)
class BusStopAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'code')
    search_fields = ('name', 'city', 'code')