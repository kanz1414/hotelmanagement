from django.shortcuts import render, redirect, get_object_or_404
from .models import Hotels, Rooms, Reservation
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime

def homepage(request):
    all_location = Hotels.objects.values_list('location', 'id').distinct()
    rooms = Rooms.objects.filter(status="available")

    if request.method == "POST":
        hotel_id = request.POST.get('search_location')
        capacity = request.POST.get('capacity')
        cin = request.POST.get('cin')
        cout = request.POST.get('cout')

        # ✅ Validate inputs
        if not (hotel_id and capacity and cin and cout):
            messages.error(request, "Please fill all fields")
            return redirect('home')

        try:
            capacity = int(capacity)
            cin = datetime.strptime(cin, "%Y-%m-%d").date()
            cout = datetime.strptime(cout, "%Y-%m-%d").date()
        except:
            messages.error(request, "Invalid input")
            return redirect('home')

        # ✅ Date validation
        if cin >= cout:
            messages.error(request, "Check-out must be after check-in")
            return redirect('home')

        # ✅ Get hotel safely
        try:
            hotel = Hotels.objects.get(id=hotel_id)
        except Hotels.DoesNotExist:
            messages.error(request, "Invalid location selected")
            return redirect('home')

        # ✅ Find reserved rooms
        reserved_rooms = Reservation.objects.filter(
            room__hotel=hotel,
            check_in__lt=cout,
            check_out__gt=cin
        ).values_list('room_id', flat=True)

        # ✅ Filter available rooms (REAL LOGIC)
        rooms = Rooms.objects.filter(
            hotel=hotel,
            capacity__gte=capacity,   # 🔥 IMPORTANT CHANGE
            status="available"
        ).exclude(id__in=reserved_rooms)

        # ✅ If no rooms
        if not rooms.exists():
            messages.warning(request, "No rooms available for selected dates")

    return render(request, 'index.html', {
        'rooms': rooms,
        'all_location': all_location
    })


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Please enter username and password")
            return redirect('login')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'user/userlogin.html')


def user_signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # ❌ Check empty fields
        if not username or not password1 or not password2:
            messages.error(request, "All required fields must be filled")
            return redirect('signup')

        # ❌ Username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        # ❌ Password match
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        # ✅ Create user
        user = User.objects.create_user(
            username=username,
            password=password1,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'user/userlogin.html')


def logout_page(request):
    logout(request)
    return redirect('home')


def room_details(request, id):
    room = get_object_or_404(Rooms, id=id)
    return render(request, 'staff/viewroom.html', {'room': room})


@login_required(login_url='/login/')
def book_room_page(request):
    room = get_object_or_404(Rooms, id=request.GET.get('roomid'))
    return render(request, 'user/bookroom.html', {'room': room})


@login_required(login_url='/login/')
def book_room(request):
    if request.method == "POST":
        room = get_object_or_404(Rooms, id=request.POST.get('room_id'))

        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        # Convert to date
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()

        # ❌ Check date validity
        if check_out_date <= check_in_date:
            messages.error(request, "Check-out must be after check-in")
            return redirect('room_details', id=room.id)

        # ❌ Check overlapping booking
        if Reservation.objects.filter(
            room=room,
            check_in__lt=check_out_date,
            check_out__gt=check_in_date
        ).exists():
            messages.error(request, "Room already booked for selected dates")
            return redirect('home')

        # ✅ Create booking
        reservation=Reservation.objects.create(
            guest=request.user,
            room=room,
            check_in=check_in_date,
            check_out=check_out_date
        )

        messages.success(request, "Room booked successfully")
        return redirect('confirmation', reservation.id)

def contactpage(request):
    return render(request, 'contact.html')



@login_required(login_url='/login/')
def user_dashboard(request):
    bookings = Reservation.objects.filter(guest=request.user)
    return render(request, 'user/mybookings.html', {'bookings': bookings})

def booking_confirmation(request,id):
    reservation=Reservation.objects.get(id=id)
    return render(request, 'user/confirmation.html',{'booking':reservation})
