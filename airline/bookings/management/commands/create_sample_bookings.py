from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bookings.models import Booking
from datetime import date, timedelta
import random
import string

class Command(BaseCommand):
    help = 'Create sample bookings for testing'

    def handle(self, *args, **options):
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created test user: {user.username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Test user already exists: {user.username}')
            )

        # Clear existing bookings for this user
        Booking.objects.filter(user=user).delete()
        self.stdout.write('Cleared existing bookings for test user')

        # Create sample bookings
        sample_bookings = [
            {
                'flight_code': 'VA882',
                'origin': 'SGN',
                'destination': 'HAN',
                'depart_date': date.today() + timedelta(days=7),
                'return_date': date.today() + timedelta(days=14),
                'trip_type': 'return',
                'cabin_class': 'Economy',
                'adults': 2,
                'children': 1,
                'selected_seats': ['12A', '12B', '12C'],
                'adult_price': 299.00,
                'child_price': 224.25,
                'seat_fees': 75.00,
                'taxes': 89.14,
                'total_amount': 1086.39,
                'status': 'confirmed'
            },
            {
                'flight_code': 'VN123',
                'origin': 'HAN',
                'destination': 'DAD',
                'depart_date': date.today() + timedelta(days=15),
                'return_date': None,
                'trip_type': 'oneway',
                'cabin_class': 'Business',
                'adults': 1,
                'children': 0,
                'selected_seats': ['1A'],
                'adult_price': 747.50,
                'child_price': 0.00,
                'seat_fees': 25.00,
                'taxes': 115.88,
                'total_amount': 888.38,
                'status': 'confirmed'
            },
            {
                'flight_code': 'BL456',
                'origin': 'SGN',
                'destination': 'PQC',
                'depart_date': date.today() + timedelta(days=30),
                'return_date': date.today() + timedelta(days=37),
                'trip_type': 'return',
                'cabin_class': 'Premium Economy',
                'adults': 1,
                'children': 2,
                'selected_seats': ['8D', '8E', '8F'],
                'adult_price': 448.50,
                'child_price': 336.38,
                'seat_fees': 75.00,
                'taxes': 128.53,
                'total_amount': 988.41,
                'status': 'pending'
            }
        ]

        created_count = 0
        for booking_data in sample_bookings:
            booking = Booking.objects.create(
                user=user,
                **booking_data
            )
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created booking: {booking.booking_reference} - {booking.flight_code}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample bookings!')
        )
        self.stdout.write(
            self.style.WARNING('You can now login with username: testuser, password: testpass123')
        )
