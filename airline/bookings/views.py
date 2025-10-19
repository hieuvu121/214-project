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

def parse_selected_seats(selected_seats_str):
    """Safely parse selected seats from various formats"""
    if not selected_seats_str or selected_seats_str.strip() == '':
        return []
    
    # Try to parse as JSON first
    try:
        return json.loads(selected_seats_str)
    except (json.JSONDecodeError, TypeError):
        pass
    
    # If JSON parsing fails, try to parse as comma-separated string
    try:
        if isinstance(selected_seats_str, str):
            # Remove brackets and quotes if present
            cleaned = selected_seats_str.strip('[]"\'')
            if cleaned:
                # Split by comma and clean each seat
                seats = [seat.strip().strip('"\'') for seat in cleaned.split(',') if seat.strip()]
                return seats
    except:
        pass
    
    # If all else fails, return empty list
    return []

@login_required(login_url='/auth/login/')
@require_http_methods(["POST"])
def payment(request):
    """Handle payment process - requires authentication"""
    # Process payment (simplified for demo)
    # In real implementation, you'd integrate with payment gateway
    
    print(f"Payment request received from user: {request.user}")
    print(f"Request method: {request.method}")
    print(f"POST data: {request.POST}")
    
    # Get booking details from POST data
    flight_code = request.POST.get('flight_code')
    origin = request.POST.get('origin')
    destination = request.POST.get('destination')
    depart_date_str = request.POST.get('depart_date')
    return_date_str = request.POST.get('return_date')
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
    
    # Parse dates - handle different possible formats
    from datetime import datetime
    try:
        # Try different date formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
            try:
                depart_date = datetime.strptime(depart_date_str, fmt).date()
                break
            except ValueError:
                continue
        else:
            # If no format works, use today's date
            depart_date = datetime.now().date()
    except:
        depart_date = datetime.now().date()
    
    return_date = None
    if return_date_str and return_date_str.strip():
        try:
            # Try different date formats for return date
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    return_date = datetime.strptime(return_date_str, fmt).date()
                    break
                except ValueError:
                    continue
        except:
            return_date = None
    
    try:
        # Debug: Print received data
        print(f"Payment data received:")
        print(f"Flight code: {flight_code}")
        print(f"Origin: {origin}")
        print(f"Destination: {destination}")
        print(f"Depart date: {depart_date}")
        print(f"Return date: {return_date}")
        print(f"Trip type: {trip_type}")
        print(f"Cabin class: {cabin_class}")
        print(f"Adults: {adults}")
        print(f"Children: {children}")
        print(f"Selected seats (raw): '{selected_seats}'")
        print(f"Selected seats (type): {type(selected_seats)}")
        parsed_seats = parse_selected_seats(selected_seats)
        print(f"Selected seats (parsed): {parsed_seats}")
        print(f"Adult price: {adult_price}")
        print(f"Child price: {child_price}")
        print(f"Seat fees: {seat_fees}")
        print(f"Taxes: {taxes}")
        print(f"Total amount: {total_amount}")
        
        # Create booking record
        booking = Booking.objects.create(
            user=request.user,
            flight_code=flight_code,
            origin=origin,
            destination=destination,
            depart_date=depart_date,
            return_date=return_date,
            trip_type=trip_type,
            cabin_class=cabin_class,
            adults=adults,
            children=children,
            selected_seats=parse_selected_seats(selected_seats),
            adult_price=adult_price,
            child_price=child_price,
            seat_fees=seat_fees,
            taxes=taxes,
            total_amount=total_amount,
            status='confirmed'
        )
        
        print(f"Booking created successfully: {booking.booking_reference}")
        
        # Return JSON response for popup
        return JsonResponse({
            'success': True,
            'message': f'Payment successful! Your booking reference is {booking.booking_reference}',
            'booking_reference': booking.booking_reference,
            'total_amount': total_amount,
            'redirect_url': '/'
        })
        
    except Exception as e:
        print(f"Payment error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Payment failed: {str(e)}'
        })

def manage_bookings(request):
    """Show user's bookings - requires authentication"""
    if not request.user.is_authenticated:
        return redirect(f'/auth/login/?next={reverse("manage_bookings")}')
    
    # Filter out cancelled bookings from the main view
    bookings = Booking.objects.filter(user=request.user).exclude(status='cancelled').order_by('-created_at')
    
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

@login_required(login_url='/auth/login/')
@require_http_methods(["POST"])
def cancel_booking(request, booking_id):
    """Cancel a booking - requires authentication"""
    try:
        # Get the booking and verify ownership
        booking = Booking.objects.get(id=booking_id, user=request.user)
        
        # Check if booking can be cancelled
        if booking.status not in ['confirmed', 'pending']:
            return JsonResponse({
                'success': False,
                'message': f'Cannot cancel booking with status: {booking.get_status_display()}'
            })
        
        # Update booking status to cancelled
        booking.status = 'cancelled'
        booking.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Booking {booking.booking_reference} has been cancelled successfully.',
            'booking_reference': booking.booking_reference
        })
        
    except Booking.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Booking not found or you do not have permission to cancel it.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error cancelling booking: {str(e)}'
        })

@login_required(login_url='/auth/login/')
def cancelled_bookings(request):
    """Get cancelled bookings for AJAX request"""
    try:
        # Get only cancelled bookings
        cancelled_bookings = Booking.objects.filter(user=request.user, status='cancelled').order_by('-created_at')
        
        # Add calculated fields to each booking
        for booking in cancelled_bookings:
            booking.adults_subtotal = float(booking.adult_price) * booking.adults
            booking.children_subtotal = float(booking.child_price) * booking.children
            booking.flight_subtotal = booking.adults_subtotal + booking.children_subtotal
        
        # Render the cancelled bookings HTML
        from django.template.loader import render_to_string
        html = render_to_string('bookings/cancelled_bookings_list.html', {
            'bookings': cancelled_bookings
        })
        
        return JsonResponse({
            'success': True,
            'bookings': list(cancelled_bookings.values('id', 'booking_reference', 'flight_code', 'status')),
            'html': html
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error loading cancelled bookings: {str(e)}'
        })