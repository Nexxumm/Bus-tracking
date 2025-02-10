from django.db import transaction
from django.utils import timezone
from Dvm import settings
from .models import *
from django.core.mail import send_mail
from django.urls import reverse


def create_booking(user, bus, seat_class,passengers_data ,travel_date):
    if not bus.is_scheduled_on_date(travel_date):
        raise ValueError("Invalid travel date")

    validate_seat_availability(bus, seat_class, len(passengers_data))
    total_cost = bus.base_fare * seat_class.fare_multiplier * len(passengers_data)

    if user.wallet_balance < total_cost:
            raise ValueError("Not enough wallet balance")

    booking = {
        'user' : user,
        'bus' : bus,
        'seat_class' : seat_class ,
        'num_seats' : len(passengers_data),
        'travel_date' : travel_date,
        'total_cost' : total_cost,
    }
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

    user.wallet_balance -= total_cost
    user.save()

    return booking


def send_otp_email(user, purpose='registration'):
    otp = OTP.objects.create(
        user=user,
        code=generate_random_code(),
        expires_at=timezone.now() + timezone.timedelta(minutes=10)
    )
    verification_url = f"{settings.SITE_URL}{reverse('verify_otp')}?token={otp.generate_token()}"
    send_mail(
        'OTP Verification',
        f'Your OTP is {otp.code} or verify here: {verification_url}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )

def validate_seat_availability(bus, seat_class, num_passengers):
    bus_seat_class = BusSeatClass.objects.get(bus=bus, seat_class=seat_class)
    if bus_seat_class.available_seats < num_passengers:
        raise ValueError(f"Only {bus_seat_class.available_seats} seats left in {seat_class.name} class")