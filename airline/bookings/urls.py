from django.urls import path
from . import views
urlpatterns=[
    path('book/',views.booking,name='book'),
    path('summary/',views.summary,name='summary'),
]