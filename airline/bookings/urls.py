from django.urls import path
from . import views
urlpatterns=[
    path('book/',views.booking,name='book'),
    path('food-drinks/',views.food_drinks_selection,name='food_drinks_selection'),
    path('update-food-selection/',views.update_food_selection,name='update_food_selection'),
    path('summary/',views.summary,name='summary'),
    path('payment/',views.payment,name='payment'),
    path('manage/',views.manage_bookings,name='manage_bookings'),
    path('cancel/<int:booking_id>/',views.cancel_booking,name='cancel_booking'),
    path('cancelled/',views.cancelled_bookings,name='cancelled_bookings'),
]