from django.db import models
from django.contrib.auth.models import User


# Hotel Model
class Hotels(models.Model):
    name = models.CharField(max_length=30)
    owner = models.CharField(max_length=20)
    location = models.CharField(max_length=50)
    state = models.CharField(max_length=50, )
    country = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# Room Model (with Image)
class Rooms(models.Model):

    ROOM_STATUS = (
        ("available", "Available"),
        ("not_available", "Not Available"),
    )

    ROOM_TYPE = (
        ("premium", "Premium"),
        ("deluxe", "Deluxe"),
        ("regular", "Regular"),
    )

    room_type = models.CharField(max_length=20, choices=ROOM_TYPE)
    capacity = models.IntegerField()
    price = models.IntegerField()
    size = models.IntegerField()
    hotel = models.ForeignKey(Hotels, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ROOM_STATUS)
    room_number = models.IntegerField()
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number}"


# Reservation Model
class Reservation(models.Model):
    check_in = models.DateField()
    check_out = models.DateField()
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE)
    guest = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.guest.username} - {self.room}"

    # Extra: calculate stay duration
    def total_days(self):
        return (self.check_out - self.check_in).days