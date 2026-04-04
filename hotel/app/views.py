from django.shortcuts import render ,redirect
from django.http import HttpResponse , HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from broomk.models import Hotels, Rooms, Reservation

#staff login and signup page

def staff_sign_up(request):
    if request.method == "POST":
        user_name = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        #  Empty validation
        if not user_name or not password1 or not password2:
            messages.warning(request, "All fields are required")
            return redirect('staffsignup')

        # Password match
        if password1 != password2:
            messages.warning(request, "Passwords do not match")
            return redirect('staffsignup')

        # Username exists check
        if User.objects.filter(username=user_name).exists():
            messages.warning(request, "Username already exists")
            return redirect('staffsignup')

        # Create staff user
        user = User.objects.create_user(
            username=user_name,
            password=password1
        )
        user.is_active = False
        user.save()

        messages.success(request, "Staff Registration Successful")
        return redirect("staffloginpage")

    return render(request, 'staff/stafflogin.html')

# Create your views here.
from django.contrib.auth.models import User

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Step 1: Check if user exists
        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Incorrect username or password")
            return redirect('staffloginpage')

        # Step 2: Check password
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('staffpanel')
            else:
                messages.error(request, "You are not staff")
                return redirect('staffloginpage')

        else:
            # Handle inactive user separately
            if not user_obj.is_active:
                messages.error(request, "Your account is blocked. Contact admin.")
            else:
                messages.error(request, "Incorrect username or password")

            return redirect('staffloginpage')

    return render(request, 'staff/stafflogin.html')



#staff panel page
@login_required(login_url='/staff')
def panel(request):
    
    if request.user.is_staff == False:
        return HttpResponse('Access Denied')
    
    rooms = Rooms.objects.all()
    total_rooms = len(rooms)
    available_rooms = len(Rooms.objects.all().filter(status='available'))
    unavailable_rooms = len(Rooms.objects.all().filter(status='not avaialable'))
    reserved = len(Reservation.objects.all())

    hotel = Hotels.objects.values_list('location','id').distinct().order_by()

    return render(request,'staff/panel.html',{'location':hotel,
                                                  'reserved':reserved,
                                                  'rooms':rooms,
                                                  'total_rooms':total_rooms,
                                                  'available':available_rooms,
                                                  'unavailable':unavailable_rooms,                                   
                                                    'rooms': rooms,
                                                'room_types': Rooms.ROOM_TYPE,     
                                                'room_status': Rooms.ROOM_STATUS, })



@login_required(login_url='/staff')
def view_room(request, id):

    if not request.user.is_staff:
        return HttpResponse("Access Denied")

    room = get_object_or_404(Rooms, id=id)
    reservations = Reservation.objects.filter(room=room)


    return render(request, 'staff/viewroom.html', {
        'room': room,
        'reservations':reservations
    })

#for adding room
@login_required(login_url='/staff')
def add_new_room(request):
    if not request.user.is_staff:
        return HttpResponse('Access Denied')

    if request.method == "POST":
        try:
            hotel_id = request.POST.get('hotel')

            if not hotel_id:
                messages.error(request, "Hotel is required")
                return redirect('addroom')

            hotel = get_object_or_404(Hotels, id=hotel_id)

            room_number = request.POST.get('roomno')
            room_type = request.POST.get('roomtype')
            capacity = request.POST.get('capacity')
            size = request.POST.get('size')
            status = request.POST.get('status')
            price = request.POST.get('price')

            # Validate required fields
            if not all([room_number, room_type, capacity, size, status, price]):
                messages.error(request, "All fields are required")
                return redirect('addroom')

            Rooms.objects.create(
                room_number=int(room_number),
                room_type=room_type,
                capacity=int(capacity),
                size=int(size),
                hotel=hotel,
                status=status,
                price=int(price)
            )

            messages.success(request, "New Room Added Successfully")
            return redirect('staffpanel')

        except ValueError:
            messages.error(request, "Invalid numeric values")
            return redirect('addroom')

    # GET request → show form
    hotels = Hotels.objects.all()
    return render(request, 'staff/addroom.html', {
        'hotels': hotels,
        'room_types': Rooms.ROOM_TYPE,
        'room_status': Rooms.ROOM_STATUS,
    })

@login_required(login_url='/staff')
def edit_room(request):
    # Only allow staff
    if not request.user.is_staff:
        return HttpResponse('Access Denied')

    if request.method == 'POST':
        room_id = request.POST.get('roomid')
        hotel_id = request.POST.get('hotel')

        # Validate IDs
        if not room_id or not hotel_id:
            messages.error(request, "Invalid data")
            return redirect('staffpanel')

        room = get_object_or_404(Rooms, id=room_id)
        hotel = get_object_or_404(Hotels, id=hotel_id)

        try:
            # Update fields safely
            room.room_type = request.POST.get('roomtype', room.room_type)
            room.capacity = int(request.POST.get('capacity', room.capacity))
            room.price = int(request.POST.get('price', room.price))
            room.size = int(request.POST.get('size', room.size))
            room.status = request.POST.get('status', room.status)
            image=request.FILES.get('image')
            if image:
                room.image=image
            room.hotel = hotel
            room.save()

            messages.success(request, "Room Details Updated Successfully")
            return redirect('staffpanel')

        except ValueError:
            messages.error(request, "Invalid numeric values")
            return redirect('staffpanel')

    else:
        #  GET request
        room_id = request.GET.get('roomid')

        if not room_id:
            messages.error(request, "Room ID missing")
            return redirect('staffpanel')

        room = get_object_or_404(Rooms, id=room_id)
        hotels = Hotels.objects.all()

        return render(request, 'staff/editroom.html', {
            'room': room,
            'hotels': hotels,  # for dropdown
            'room_types': Rooms.ROOM_TYPE,
            'room_status': Rooms.ROOM_STATUS,
        })

def delete_room(request,id):
    room=get_object_or_404(Rooms,id=id)
    room.delete()
    return redirect('staffpanel')



@login_required(login_url='/staff')
def add_new_location(request):
    if request.method == "POST" and request.user.is_staff:
        hname = request.POST.get('new_hotel')
        owner = request.POST.get('new_owner')
        location = request.POST.get('new_city')
        state = request.POST.get('new_state')
        country = request.POST.get('new_country')
        
        hotels = Hotels.objects.all().filter(name = hname)
        if hotels:
            messages.warning(request,"Sorry City at this Location already exist")
            return redirect("staffpanel")
        else:
            new_hotel = Hotels()
            new_hotel.name = hname
            new_hotel.owner = owner
            new_hotel.location = location
            new_hotel.state = state
            new_hotel.country = country
            new_hotel.save()
            messages.success(request,"New Location Has been Added Successfully")
            return redirect("staffpanel")

    else:
        return HttpResponse("Not Allowed")
    
#for showing all bookings to staff
@login_required(login_url='/staff')
def all_bookings(request):
   
    bookings = Reservation.objects.all()
    if not bookings:
        messages.warning(request,"No Bookings Found")
    return render(request,'staff/allbookings.html',{'bookings':bookings})
    

def customers(request):
    users=User.objects.filter(is_staff=False)
    return render(request, 'staff/customers.html', {'users':users})
        
def staffs(request):
    users=User.objects.filter(is_staff=True , is_superuser=False)
    return render(request, 'staff/staffs.html',{'users':users})

def update_status(request, id):
    user=get_object_or_404(User,id=id)
    if user.is_active:
        user.is_active=False
    else:
        user.is_active=True
    user.save()
    return redirect(staffs)