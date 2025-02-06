from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('CONSUMER', 'Consumer'),
        ('ADMIN', 'Administrator'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(choices=USER_TYPE_CHOICES, max_length=10, default='PASSENGER')
    wallet_balance = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}({self.user_type})"

class Day(models.Model):
    name = models.CharField(max_length=10)
    number = models.IntegerField(unique=True) # 0 is monday

    def __str__(self):
        return self.name

class Bus(models.Model):
    number = models.CharField(max_length=50)
    departure = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    total_seats = models.PositiveIntegerField()
    fare = models.PositiveIntegerField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    scheduled_days = models.ManyToManyField(Day, through='BusSchedule')

    def is_scheduled_on_date(self, date):
        return self.scheduled_days.filter(number=date.weekday()).exists()

    def get_available_seats(self, date):
        confirmed_bookings = self.booking_set.filter(date=date , status=Booking.status.ACCEPTED)
        booked_seats = sum(booking.tickets.count() for booking in confirmed_bookings)
        return self.total_seats - booked_seats

    def __str__(self):
        return f"Bus {self.number}: {self.departure} to {self.destination}"

class BusSchedule(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    class Meta:
        unique_together = ('bus', 'day') # makes sure same bus not counted twice

class Booking(models.Model):
    STATUS_CHOICES = [
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    travel_date = models.DateField()
    booking_time = models.DateTimeField(auto_now_add=True)
    total_cost = models.PositiveIntegerField()
    status = models.CharField(choices=STATUS_CHOICES, default='ACCEPTED', max_length=10)

    def __str__(self):
        return f"{self.id}by {self.user.username}"

    def can_be_cancelled(self):
        departure_time = timezone.make_aware(
            timezone.datetime.combine(self.travel_date, self.bus.departure_time)
        )
        return timezone.now() < departure_time - timedelta(hours=6)

    def cancel(self):
        if self.status == Booking.status.ACCEPTED and self.can_be_cancelled():
            self.user.wallet_balance += self.total_cost
            self.user.save()
            self.status = Booking.status.REJECTED
            self.save()

    def save(self):
        if not self.bus.is_scheduled_on_date(self.travel_date):
            raise ValueError("Bus does not have a schedule on that date")

        if self.bus.get_available_seats(self.travel_date) < self.tickets.count():
            raise ValueError("Bus does not have enough available seats")

        super().save(*args, **kwargs)



class Ticket(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=50)
    passenger_age = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.passenger_name} ({self.passenger_age})"