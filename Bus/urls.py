from django.urls import path
from .views import BusSearchView, BookingCreateView, cancel_booking

urlpatterns = [
    # Bus Search
    path('', BusSearchView.as_view(), name='search_results'),

    # Booking Management
    path('book/<int:bus_id>/', BookingCreateView.as_view(), name='create_booking'),
    path('booking/<int:pk>/cancel/', cancel_booking, name='cancel_booking'),

    # Ticket Management
    path('booking/<int:pk>/edit-tickets/', TicketUpdateView.as_view(), name='edit_tickets'),
]