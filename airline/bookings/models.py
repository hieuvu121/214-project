from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Flight Details
    flight_code = models.CharField(max_length=10)
    origin = models.CharField(max_length=10)
    destination = models.CharField(max_length=10)
    depart_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    trip_type = models.CharField(max_length=10, choices=[('oneway', 'One Way'), ('return', 'Return')])
    cabin_class = models.CharField(max_length=20)
    
    # Passenger Details
    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)
    selected_seats = models.JSONField(default=list, blank=True)
    
    # Pricing
    adult_price = models.DecimalField(max_digits=10, decimal_places=2)
    child_price = models.DecimalField(max_digits=10, decimal_places=2)
    seat_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxes = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Booking Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_reference = models.CharField(max_length=10, unique=True, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking {self.booking_reference} - {self.flight_code}"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            # Generate a unique booking reference
            import random
            import string
            self.booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)