from django.db import models
from django.contrib.auth.models import User

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    travel_date = models.DateField()
    booking_time = models.DateTimeField(auto_now_add=True)
    total_cost = models.PositiveIntegerField()
    status = models.CharField(choices=STATUS_CHOICES, default='ACCEPTED', max_length=10)

    def __str__(self):
        return f"{self.id}by {self.user.username}"

class Ticket(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=50)
    passenger_age = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.passenger_name} ({self.passenger_age})"