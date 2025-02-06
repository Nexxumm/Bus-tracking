from django.utils import timezone
from models import *

def create_booking(user, bus, travel_date , passengers):
    if not bus.is_scheduled_on_date(travel_date):
        raise ValueError("Invalid travel date")

    available_seats = bus.get_available_seats(travel_date)

    if available_seats < len(passengers):
        raise ValueError("Not enough available seats")

    total_cost = bus.bus_fare * len(passengers)

    if user.wallet_balance < total_cost:
        raise ValueError("Not enough wallet balance")

    booking = {
        'user' : user,
        'bus' : bus,
        'travel_date' : travel_date,
        'total_cost' : total_cost,

    }

    Ticket.objects.bulk_create([
        Ticket(
            booking = booking,
            passenger_name = passengers['name'],
            passenger_age = passengers['age'],

        ) for passenger in passengers
    ])

    user.wallet_balance -= total_cost
    user.save()

    return booking