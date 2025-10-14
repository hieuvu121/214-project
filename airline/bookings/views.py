from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
# Create your views here.
def booking(request):
    code   = request.GET.get('code', 'VA882')
    cabin  = request.GET.get('cabin', 'Economy')
    adults = int(request.GET.get('adults', 1) or 1)
    children = int(request.GET.get('children', 0) or 0)
    max_select = adults + children

    booked = {
        '3C','4D','7A','12B','12C','14E','15F','18A','18B','22C','23D','24E','28F'
    }
    rows = list(range(1, 31))
    left_block  = ['A','B','C']
    right_block = ['D','E','F']
    context = {
        'flight_code': code,
        'cabin': cabin,
        'max_select': max_select,
        'booked': booked,
        'rows': rows,
        'left_block': left_block,
        'right_block': right_block,
        'adults': adults,
        'children': children,
        'origin': request.GET.get('from', ''),
        'dest': request.GET.get('to', ''),
        'depart': request.GET.get('depart', ''),
        'trip': request.GET.get('trip', 'return'),
    }
    return render(request, 'seatSelection.html', context)

class homeView(TemplateView):
    template_name='home.html'