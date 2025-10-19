from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'user', 'flight_code', 'origin', 'destination', 'depart_date', 'status', 'total_amount']
    list_filter = ['status', 'trip_type', 'cabin_class', 'depart_date']
    search_fields = ['booking_reference', 'flight_code', 'user__username', 'user__email']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_reference', 'user', 'status')
        }),
        ('Flight Details', {
            'fields': ('flight_code', 'origin', 'destination', 'depart_date', 'return_date', 'trip_type', 'cabin_class')
        }),
        ('Passenger Details', {
            'fields': ('adults', 'children', 'selected_seats')
        }),
        ('Pricing', {
            'fields': ('adult_price', 'child_price', 'seat_fees', 'taxes', 'total_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
