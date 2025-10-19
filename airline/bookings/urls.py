from django.urls import path
from . import views
urlpatterns=[
    path('book/',views.booking,name='book'),
    path('summary/',views.summary,name='summary'),
    path('payment/',views.payment,name='payment'),
    path('manage/',views.manage_bookings,name='manage_bookings'),
    path('cancel/<int:booking_id>/',views.cancel_booking,name='cancel_booking'),
    path('cancelled/',views.cancelled_bookings,name='cancelled_bookings'),
]