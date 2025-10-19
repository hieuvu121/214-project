from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Booking
import json
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

@login_required(login_url='/auth/login/')
@require_http_methods(["POST"])
def payment(request):
    """Handle payment process - requires authentication"""
    # Process payment (simplified for demo)
    # In real implementation, you'd integrate with payment gateway
    
    # Get booking details from POST data
    flight_code = request.POST.get('flight_code')
    origin = request.POST.get('origin')
    destination = request.POST.get('destination')
    depart_date = request.POST.get('depart_date')
    return_date = request.POST.get('return_date')
    trip_type = request.POST.get('trip_type')
    cabin_class = request.POST.get('cabin_class')
    adults = int(request.POST.get('adults', 1))
    children = int(request.POST.get('children', 0))
    selected_seats = request.POST.get('selected_seats', '[]')
    adult_price = float(request.POST.get('adult_price', 299))
    child_price = float(request.POST.get('child_price', 224))
    seat_fees = float(request.POST.get('seat_fees', 0))
    taxes = float(request.POST.get('taxes', 0))
    total_amount = float(request.POST.get('total_amount', 0))
    
    try:
        # Create booking record
        booking = Booking.objects.create(
            user=request.user,
            flight_code=flight_code,
            origin=origin,
            destination=destination,
            depart_date=depart_date,
            return_date=return_date if return_date else None,
            trip_type=trip_type,
            cabin_class=cabin_class,
            adults=adults,
            children=children,
            selected_seats=json.loads(selected_seats),
            adult_price=adult_price,
            child_price=child_price,
            seat_fees=seat_fees,
            taxes=taxes,
            total_amount=total_amount,
            status='confirmed'
        )
        
        # Return JSON response for popup
        return JsonResponse({
            'success': True,
            'message': f'Payment successful! Your booking reference is {booking.booking_reference}',
            'booking_reference': booking.booking_reference,
            'total_amount': total_amount,
            'redirect_url': '/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Payment failed. Please try again.'
        })

def manage_bookings(request):
    """Show user's bookings - requires authentication"""
    if not request.user.is_authenticated:
        return redirect(f'/auth/login/?next={reverse("manage_bookings")}')
    
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    
    # Add calculated fields to each booking
    for booking in bookings:
        booking.adults_subtotal = float(booking.adult_price) * booking.adults
        booking.children_subtotal = float(booking.child_price) * booking.children
        booking.flight_subtotal = booking.adults_subtotal + booking.children_subtotal
    
    context = {
        'bookings': bookings,
        'user': request.user
    }
    
    return render(request, 'bookings/manage_bookings.html', context)