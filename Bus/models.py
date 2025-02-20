from datetime import timedelta, datetime
import pyotp
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    USER_TYPE_CHOICES = [
        ('CONSUMER', 'Consumer'),
        ('ADMIN', 'Administrator'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(choices=USER_TYPE_CHOICES, max_length=10, default='PASSENGER')
    wallet_balance = models.PositiveIntegerField(default=0)
    email_otp = models.CharField(max_length=6,null=True, blank=True)
    def __str__(self):
        return f"{self.user.username}({self.user_type})"

class Day(models.Model):
    name = models.CharField(max_length=10)
    number = models.IntegerField(unique=True) # 0 is monday

    def __str__(self):
        return self.name


class BusStop(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    code = models.CharField(max_length=10 ,unique=True)

    def __str__(self):
        return self.name

class Route(models.Model):
    name = models.CharField(max_length=100)
    fare = models.PositiveIntegerField()
    stops = models.ManyToManyField(BusStop, through='RouteStop')

    def __str__(self):
        return self.name

class RouteStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    stop = models.ForeignKey(BusStop, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.stop.name

    class Meta:
        ordering = ['order']
        unique_together = [('route','order'),('route', 'stop')]


class SeatClass(models.Model):
    CLASS_CHOICES = [
        ('GENERAL', 'General'),
        ('SLEEPER', 'Sleeper'),
        ('LUXURY', 'Luxury'),
    ]
    name = models.CharField(max_length=20, choices=CLASS_CHOICES, unique=True)
    fare_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)

    def __str__(self):
        return self.name



class BusSeatClass(models.Model):
    bus = models.ForeignKey('Bus', on_delete=models.CASCADE, related_name='bus_seat_classes')
    seat_class = models.ForeignKey(SeatClass, on_delete=models.CASCADE)
    total_seats = models.PositiveIntegerField()
    booked_seats = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.seat_class.name

    @property
    def available_seats(self):
        return self.total_seats - self.booked_seats

    @property
    def total_fare(self):
        return self.bus.fare * self.seat_class.fare_multiplier


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
    seat_classes = models.ManyToManyField(SeatClass, through=BusSeatClass)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=True)


    def is_scheduled_on_date(self, date):
        # Convert date from string (in dd-mm-yyyy format) to a date object if necessary
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()
        return self.scheduled_days.filter(number=date.weekday()).exists()

    def get_available_seats(self, date):
        confirmed_bookings = self.booking_set.filter(travel_date=date , status=Booking.ACCEPTED)
        booked_seats = sum(booking.tickets.count() for booking in confirmed_bookings)
        return self.total_seats - booked_seats

    def get_scheduled_days(self):
        return ", ".join([day.name for day in self.scheduled_days.all()])

    def __str__(self):
        return f"Bus {self.number}: {self.departure} to {self.destination}"

class BusSchedule(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    class Meta:
        unique_together = ('bus', 'day') # makes sure same bus not counted twice



class Booking(models.Model):
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'

    STATUS_CHOICES = [
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    google_id = models.CharField(max_length=255, blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    start_stop = models.ForeignKey('BusStop',related_name='start_booking' ,on_delete=models.PROTECT)
    end_stop = models.ForeignKey('BusStop',related_name='end_booking',on_delete=models.PROTECT)
    travel_date = models.DateField()
    booking_time = models.DateTimeField(auto_now_add=True)
    total_cost = models.PositiveIntegerField()
    status = models.CharField(choices=STATUS_CHOICES, default='ACCEPTED', max_length=10)
    seat_class = models.ForeignKey(SeatClass, on_delete=models.PROTECT, blank=True, null=True)
    @property
    def num_passengers(self):
        return self.tickets.count()

    def __str__(self):
        return f"{self.id}by {self.user.username}"

    def can_be_cancelled(self):
        departure_time = timezone.make_aware(
            timezone.datetime.combine(self.travel_date, self.bus.departure_time)
        )
        return timezone.now() < departure_time - timedelta(hours=6)

    def cancel(self):
        if self.status == Booking.status.ACCEPTED and self.can_be_cancelled():
            with transaction.atomic():
                bus_seat_class = BusSeatClass.objects.select_for_update().get(
                    bus = self.bus,
                    seat_class=self.tickets.first().seat_class
                )
                bus_seat_class.booked_seats -= self.tickets.count()
                bus_seat_class.save()

                self.user.profile.wallet_balance += self.total_cost
                self.user.profile.save()
                self.status = Booking.status.REJECTED
                self.save()

    def save(self, *args, **kwargs):

        if not self.bus.is_scheduled_on_date(self.travel_date):
            raise ValueError("Bus does not have a schedule on that date")

        bus_seat_class = BusSeatClass.objects.get(
            bus=self.bus,
            seat_class=self.seat_class
        )

        if self.bus.get_available_seats(self.travel_date) < bus_seat_class.available_seats:
            raise ValueError("Bus does not have enough available seats")

        super().save(*args, **kwargs)





class Ticket(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE,related_name='tickets')
    passenger_name = models.CharField(max_length=50)
    passenger_age = models.PositiveIntegerField()
    seat_class = models.ForeignKey(SeatClass, on_delete=models.PROTECT,null=True)

    def __str__(self):
        return f"{self.passenger_name} ({self.passenger_age})"




