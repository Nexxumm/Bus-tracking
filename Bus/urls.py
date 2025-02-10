from django.urls import path
from .views import *
urlpatterns = [
    path('', BusSearchView.as_view(), name='search_results'),
    path('Bus/<int:bus_id>/', BookingCreateView.as_view(), name='create_booking'),
    path('Bus/<int:pk>/cancel/', cancel_booking, name='cancel_booking'),
]