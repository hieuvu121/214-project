from django.urls import path
from . import views
urlpatterns=[
    path('',views.flightList,name='flightList'),
    path('search/',views.search,name='search'),
]