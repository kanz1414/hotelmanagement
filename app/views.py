from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from broomk.models import Hotels, Rooms, Reservation


# ------------------ STAFF SIGNUP ------------------
def staff_sign_up(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not username or not password1 or not password2:
            messages.warning(request, "All fields are required")
            return redirect('staff_signup')

        if password1 != password2:
            messages.warning(request, "Passwords do not match")
            return redirect('staff_signup')

        if User.objects.filter(username=username).exists():
            messages.warning(request, "Username already exists")
            return redirect('staff_signup')

        user = User.objects.create_user(username=username, password=password1)
        user.is_staff = True   # ✅ IMPORTANT
        user.is_active = True  # activate directly
        user.save()

        messages.success(request, "Staff registered successfully")
        return redirect("staff_login")

    return render(request, 'staff/stafflogin.html')


# ------------------ STAFF LOGIN ------------------
def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            return redirect('staff_panel')
        else:
            messages.error(request, "Invalid staff credentials")

    return render(request, 'staff/stafflogin.html')


# ------------------ DASHBOARD ------------------
@login_required(login_url='/staff/login/')
def panel(request):
    if not request.user.is_staff:
        return HttpResponse("Access Denied")

    rooms = Rooms.objects.all()

    context = {
        'rooms': rooms,
        'total_rooms': rooms.count(),
        'available': Rooms.objects.filter(status='available').count(),
        'unavailable': Rooms.objects.filter(status='not available').count(),
        'reserved': Reservation.objects.count(),
        'hotels': Hotels.objects.all(),
        'room_types': Rooms.ROOM_TYPE,
        'room_status': Rooms.ROOM_STATUS,

       
    }

    return render(request, 'staff/panel.html', context)


# ------------------ VIEW ROOM ------------------
@login_required(login_url='/staff/login/')
def view_room(request, id):
    room = get_object_or_404(Rooms, id=id)
    reservations = Reservation.objects.filter(room=room)

    return render(request, 'staff/viewroom.html', {
        'room': room,
        'reservations': reservations
    })


# ------------------ ADD ROOM ------------------
@login_required(login_url='/staff/login/')

def add_new_room(request):
    if request.method == "POST":
        try:
            hotel = get_object_or_404(Hotels, id=request.POST.get('hotel'))

            Rooms.objects.create(
                hotel=hotel,
                room_type=request.POST.get('roomtype'),
                room_number=request.POST.get('roomno'),   # ✅ added
                capacity=request.POST.get('capacity'),
                price=request.POST.get('price'),
                size=request.POST.get('size'),            # ✅ added
                status=request.POST.get('status'),
                image=request.FILES.get('image')          # ✅ fixed
            )

            messages.success(request, "Room Added Successfully")
            return redirect('staff_panel')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('staff_panel')

    return redirect('staff_panel')


# ------------------ EDIT ROOM ------------------
@login_required(login_url='/staff/login/')
def edit_room(request):
    if request.method == 'POST':
        room = get_object_or_404(Rooms, id=request.POST.get('roomid'))

        room.room_type = request.POST.get('roomtype')
        room.capacity = request.POST.get('capacity')
        room.price = request.POST.get('price')
        room.size = request.POST.get('size')   # ✅ FIXED
        room.status = request.POST.get('status')

        image = request.FILES.get('image')     # ✅ FIXED
        if image:
            room.image = image

        room.save()
        messages.success(request, "Room Updated Successfully")
        return redirect('staff_panel')

    room = get_object_or_404(Rooms, id=request.GET.get('roomid'))

    return render(request, 'staff/editroom.html', {
        'room': room,
        'hotels': Hotels.objects.all(),
        'room_types': Rooms.ROOM_TYPE,     # ✅ ADDED
        'room_status': Rooms.ROOM_STATUS,  # ✅ ADDED
    })

# ------------------ DELETE ROOM ------------------
@login_required(login_url='/staff/login/')
def delete_room(request, id):
    room = get_object_or_404(Rooms, id=id)
    room.delete()
    messages.success(request, "Room Deleted")
    return redirect('staff_panel')


# ------------------ ADD LOCATION ------------------
@login_required(login_url='/staff/login/')
def add_new_location(request):
    if request.method == "POST":
        name = request.POST.get('new_hotel')
        owner = request.POST.get('new_owner')
        city = request.POST.get('new_city')
        state = request.POST.get('new_state')
        country = request.POST.get('new_country')

        # Combine location (if your model has single field)
        location = f"{city}, {state}, {country}"

        if Hotels.objects.filter(name=name).exists():
            messages.warning(request, "Hotel already exists")
        else:
            Hotels.objects.create(
                name=name,
                owner=owner,
                location=location
            )
            messages.success(request, "Location Added Successfully")

    return redirect("staff_panel")


# ------------------ BOOKINGS ------------------
@login_required(login_url='/staff/login/')
def all_bookings(request):
    bookings = Reservation.objects.all()
    return render(request, 'staff/allbookings.html', {'bookings': bookings})


# ------------------ USERS ------------------
@login_required(login_url='/staff/login/')
def customers(request):
    users = User.objects.filter(is_staff=False)
    return render(request, 'staff/customers.html', {'users': users})


@login_required(login_url='/staff/login/')
def staffs(request):
    users = User.objects.filter(is_staff=True)
    return render(request, 'staff/staffs.html', {'users': users})


# ------------------ STATUS TOGGLE ------------------
@login_required(login_url='/staff/login/')
def update_status(request, id):
    user = get_object_or_404(User, id=id)
    user.is_active = not user.is_active
    user.save()
    return redirect('staffs')