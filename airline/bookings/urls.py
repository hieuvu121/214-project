from django.urls import path
from . import views
urlpatterns=[
    path('book/',views.booking,name='book'),
    path('summary/',views.summary,name='summary'),
    path('payment/',views.payment,name='payment'),
    path('manage/',views.manage_bookings,name='manage_bookings'),
]