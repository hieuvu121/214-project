from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
# Create your views here.
def booking(request):
    return HttpResponse('hello')

class homeView(TemplateView):
    template_name='home.html'