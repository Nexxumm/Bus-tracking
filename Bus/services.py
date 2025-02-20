from django.db import transaction
from django.utils import timezone
from Dvm import settings
from .models import *
from django.core.mail import send_mail
from django.urls import reverse


def create_booking(user, bus, seat_class, start_stop, end_stop, passengers_data, travel_date, total_cost):
    with transaction.atomic():
        if not bus.is_scheduled_on_date(travel_date):
            raise ValueError("Invalid travel date")

        validate_seat_availability(bus, seat_class, len(passengers_data))

        if user.profile.wallet_balance  < total_cost:
                raise ValueError("Not enough wallet balance")

        booking = Booking.objects.create(
            user=user,
            bus=bus,
            seat_class=seat_class,
            start_stop=start_stop,
            end_stop=end_stop,
            total_cost=total_cost,
            travel_date=travel_date,

        )
        Ticket.objects.bulk_create([
            Ticket(
                booking = booking,
                seat_class = seat_class,
                passenger_name = passenger['name'],
                passenger_age = passenger['age'],

            ) for passenger in passengers_data
        ])
        bus_seat_class = BusSeatClass.objects.select_for_update().get(
            bus=bus,
            seat_class=seat_class
        )
        bus_seat_class.booked_seats += len(passengers_data)                 #assumes same seat class for all
        bus_seat_class.save()

        user.profile.wallet_balance -= total_cost
        user.profile.save()

    return booking


def generate_otp():
    totp = pyotp.TOTP(pyotp.random_base32(), interval=300)
    return totp.now()


def verify_otp_for_user(otp, user_otp):
    return otp == user_otp

def validate_seat_availability(bus, seat_class, num_passengers):
    bus_seat_class = BusSeatClass.objects.get(bus=bus, seat_class=seat_class)
    if bus_seat_class.available_seats < num_passengers:
        raise ValueError(f"Only {bus_seat_class.available_seats} seats left in {seat_class.name} class")