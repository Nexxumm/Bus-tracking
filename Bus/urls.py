from django.urls import path
from .views import *
urlpatterns = [
    path('', BusSearchView.as_view(), name='search_results'),
    path('<int:bus_id>/<int:seat_class_id>/', BookingCreateView.as_view(), name='create_booking'),
    path('<int:pk>/cancel/', cancel_booking, name='cancel_booking'),
]