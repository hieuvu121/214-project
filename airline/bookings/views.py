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

def summary(request):
    # Get booking details from query parameters
    flight_code = request.GET.get('code', 'VA882')
    cabin = request.GET.get('cabin', 'Economy')
    adults = int(request.GET.get('adults', 1) or 1)
    children = int(request.GET.get('children', 0) or 0)
    origin = request.GET.get('from', '')
    dest = request.GET.get('to', '')
    depart = request.GET.get('depart', '')
    trip = request.GET.get('trip', 'return')
    seats = request.GET.get('seats', '')
    
    # Parse selected seats
    selected_seats = seats.split(',') if seats else []
    
    # Calculate pricing
    base_price = 299  # Base flight price
    
    # Cabin class multipliers
    cabin_multipliers = {
        'Economy': 1.0,
        'Premium Economy': 1.5,
        'Business': 2.5
    }
    
    # Calculate per passenger price based on cabin
    multiplier = cabin_multipliers.get(cabin, 1.0)
    adult_price = base_price * multiplier
    child_price = adult_price * 0.75  # Children get 25% discount
    
    # Seat selection fees
    seat_fee_per_seat = 25
    total_seat_fees = len(selected_seats) * seat_fee_per_seat
    
    # Calculate subtotals
    adults_subtotal = adults * adult_price
    children_subtotal = children * child_price
    flight_subtotal = adults_subtotal + children_subtotal
    
    # Taxes and fees (15% of flight subtotal)
    taxes = flight_subtotal * 0.15
    
    # Grand total
    grand_total = flight_subtotal + total_seat_fees + taxes
    
    context = {
        'flight_code': flight_code,
        'cabin': cabin,
        'adults': adults,
        'children': children,
        'origin': origin,
        'dest': dest,
        'depart': depart,
        'trip': trip,
        'selected_seats': selected_seats,
        'seats_str': ', '.join(selected_seats) if selected_seats else 'None',
        'adult_price': adult_price,
        'child_price': child_price,
        'adults_subtotal': adults_subtotal,
        'children_subtotal': children_subtotal,
        'flight_subtotal': flight_subtotal,
        'seat_fee_per_seat': seat_fee_per_seat,
        'total_seat_fees': total_seat_fees,
        'taxes': taxes,
        'grand_total': grand_total,
    }
    
    return render(request, 'summary.html', context)