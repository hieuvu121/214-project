from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Booking, FoodItem
import json
from decimal import Decimal, ROUND_HALF_UP

TWOPLACES = Decimal('0.01')
def as_money(x: Decimal) -> Decimal:
    return x.quantize(TWOPLACES, rounding=ROUND_HALF_UP)

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
    import re
    flight_code = request.GET.get('code', 'VA882')
    cabin = request.GET.get('cabin', 'Economy')
    adults = int(request.GET.get('adults', 1) or 1)
    children = int(request.GET.get('children', 0) or 0)
    origin = request.GET.get('from', '')
    dest = request.GET.get('to', '')
    depart = request.GET.get('depart', '')
    trip = request.GET.get('trip', 'return')
    seats = request.GET.get('seats', '')
    food_items_str = request.GET.get('food_items', '')

    # Parse selected seats
    selected_seats = seats.split(',') if seats else []

    # Parse selected food items
    selected_food_items = {}
    if food_items_str:
        try:
            selected_food_items = json.loads(food_items_str)
        except json.JSONDecodeError:
            selected_food_items = {}
    else:
        selected_food_items = request.session.get('selected_food_items', {})

    food_items_details = []
    food_drinks_total = Decimal('0.00')

    for item_id, quantity in selected_food_items.items():
        try:
            # Lấy số đầu tiên có trong key (vd: "drink_12" -> 12)
            m = re.search(r'\d+', str(item_id))
            if not m:
                continue
            fid = int(m.group())

            qty = int(quantity)
            if qty <= 0:
                continue

            food_item = FoodItem.objects.get(id=fid)
            line_total = as_money(food_item.price * qty)
            food_items_details.append({
                'item': food_item,
                'quantity': qty,
                'total_price': line_total
            })
            food_drinks_total += line_total
        except (FoodItem.DoesNotExist, ValueError, TypeError):
            continue

    food_drinks_total = as_money(food_drinks_total)

    # Pricing
    base_price = Decimal('299.00')
    cabin_multipliers = {
        'Economy': Decimal('1.00'),
        'Premium Economy': Decimal('1.50'),
        'Business': Decimal('2.50')
    }
    multiplier = cabin_multipliers.get(cabin, Decimal('1.00'))

    adult_price = as_money(base_price * multiplier)
    child_price = as_money(adult_price * Decimal('0.75'))

    seat_fee_per_seat = Decimal('25.00')
    total_seat_fees = as_money(seat_fee_per_seat * Decimal(len(selected_seats)))

    adults_subtotal = as_money(Decimal(adults) * adult_price)
    children_subtotal = as_money(Decimal(children) * child_price)
    flight_subtotal = as_money(adults_subtotal + children_subtotal)

    taxes = as_money(flight_subtotal * Decimal('0.15'))

    grand_total = as_money(flight_subtotal + total_seat_fees + food_drinks_total + taxes)

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
        'food_items_details': food_items_details,
        'food_drinks_total': food_drinks_total,
        'selected_food_items': selected_food_items,
        'taxes': taxes,
        'grand_total': grand_total,
    }
    print("DEBUG selected_food_items:", request.session.get('selected_food_items'))

    return render(request, 'summary.html', context)


def food_drinks_selection(request):
    """Food and drinks selection page"""
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
    
    # Get available food and drinks
    drinks = FoodItem.objects.filter(category='drink', is_available=True)
    foods = FoodItem.objects.filter(category='food', is_available=True)
    
    # Get selected items from session or request
    selected_items = request.session.get('selected_food_items', {})
    
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
        'drinks': drinks,
        'foods': foods,
        'selected_items': selected_items,
    }
    
    return render(request, 'food_drinks_selection.html', context)

@csrf_exempt
def update_food_selection(request):
    """Update food selection in session"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request.session['selected_food_items'] = data.get('selected_items', {})
            request.session.modified = True
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

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
    print(f"Payment request received from user: {request.user}")
    print(f"Request method: {request.method}")
    print(f"POST data: {request.POST}")

    # Basic fields
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

    # Parse money as Decimal
    adult_price = Decimal(request.POST.get('adult_price', '299'))
    child_price = Decimal(request.POST.get('child_price', '224'))
    seat_fees = Decimal(request.POST.get('seat_fees', '0'))
    food_drinks_total = Decimal(request.POST.get('food_drinks_total', '0'))
    taxes = Decimal(request.POST.get('taxes', '0'))
    total_amount = Decimal(request.POST.get('total_amount', '0'))

    # Dates
    from datetime import datetime
    try:
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
            try:
                depart_date = datetime.strptime(depart_date_str, fmt).date()
                break
            except ValueError:
                continue
        else:
            depart_date = datetime.now().date()
    except:
        depart_date = datetime.now().date()

    return_date = None
    if return_date_str and return_date_str.strip():
        try:
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    return_date = datetime.strptime(return_date_str, fmt).date()
                    break
                except ValueError:
                    continue
        except:
            return_date = None

    try:
        parsed_seats = parse_selected_seats(selected_seats)

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
            selected_seats=parsed_seats,
            adult_price=adult_price,
            child_price=child_price,
            seat_fees=seat_fees,
            food_drinks_total=food_drinks_total,
            taxes=taxes,
            total_amount=total_amount,
            status='confirmed'
        )

        return JsonResponse({
            'success': True,
            'message': f'Payment successful! Your booking reference is {booking.booking_reference}',
            'booking_reference': booking.booking_reference,
            'total_amount': str(total_amount),
            'redirect_url': '/'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'message': f'Payment failed: {str(e)}'})


def manage_bookings(request):
    if not request.user.is_authenticated:
        return redirect(f'/auth/login/?next={reverse("manage_bookings")}')

    bookings = (Booking.objects
                .filter(user=request.user)
                .exclude(status='cancelled')
                .order_by('-created_at'))

    return render(request, 'bookings/manage_bookings.html', {
        'bookings': bookings,
        'user': request.user,
    })



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
    try:
        cancelled = (Booking.objects
                     .filter(user=request.user, status='cancelled')
                     .order_by('-created_at'))

        from django.template.loader import render_to_string
        html = render_to_string('bookings/cancelled_bookings_list.html', {
            'bookings': cancelled
        })

        return JsonResponse({
            'success': True,
            'bookings': list(cancelled.values('id', 'booking_reference', 'flight_code', 'status')),
            'html': html
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading cancelled bookings: {str(e)}'})
