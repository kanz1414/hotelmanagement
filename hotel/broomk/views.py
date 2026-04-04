from django.shortcuts import render ,redirect
from django.http import HttpResponse , HttpResponseRedirect
from .models import Hotels,Rooms,Reservation
from django.contrib import messages
from django.contrib.auth import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

#homepage
def homepage(request):
    all_location = Hotels.objects.values_list('location', 'id').distinct()
    rooms = Rooms.objects.filter(status="available")

    if request.method == "POST":
        try:
            hotel_id = request.POST.get('search_location')
            capacity = request.POST.get('capacity')
            cin = request.POST.get('cin')
            cout = request.POST.get('cout')

            if hotel_id and capacity and cin and cout:

                capacity = int(capacity)
                cin = datetime.datetime.strptime(cin, "%Y-%m-%d").date()
                cout = datetime.datetime.strptime(cout, "%Y-%m-%d").date()

                hotel = Hotels.objects.filter(id=hotel_id).first()
                if not hotel:
                    messages.error(request, "Invalid hotel selected")
                    return redirect('/')

                reserved_rooms = Reservation.objects.filter(
                    room__hotel=hotel
                ).filter(
                    check_in__lt=cout,
                    check_out__gt=cin
                ).values_list('room_id', flat=True)

                rooms = Rooms.objects.filter(
                    hotel=hotel,
                    capacity=capacity,
                    status="available"
                ).exclude(id__in=reserved_rooms)

                if not rooms.exists():
                    messages.warning(request, "No rooms available")

        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'index.html', {
        'rooms': rooms,
        'all_location': all_location
    })

#about
def aboutpage(request):
    return HttpResponse(render(request,'about.html'))

def room_details(request,id):
    room=get_object_or_404(Rooms, id=id)
    return render(request,'new.html',{'room':room})

#contact page
def contactpage(request):
    return HttpResponse(render(request,'contact.html'))

#user sign up
def user_sign_up(request):
    if request.method == "POST":
        user_name = request.POST.get('username')
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Empty check
        if not user_name or not password1 or not password2:
            messages.warning(request, "All fields are required")
            return redirect('signup')

        # Password match
        if password1 != password2:
            messages.warning(request, "Passwords do not match")
            return redirect('signup')

        # Username exists check (BEST WAY)
        if User.objects.filter(username=user_name).exists():
            messages.warning(request, "Username already taken")
            return redirect('usersignup')

        # Create user
        user = User.objects.create_user(
            username=user_name,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        messages.success(request, "Registration Successful")
        return redirect('userloginpage')

    return render(request, 'userlogin.html')

#staff sign up

    

#user login and signup page
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pswd')

        user = authenticate(username=email,password=password)
        try:
            if user.is_staff:
                
                messages.error(request,"Incorrect username or Password")
                return redirect('staffloginpage')
        except:
            pass
        
        if user is not None:
            login(request,user)
            messages.success(request,"successful logged in")
            print("Login successfull")
            return redirect('homepage')
        else:
            messages.warning(request,"Incorrect username or password")
            return redirect('userloginpage')

    return render(request,'user/userlogin.html')


#logout for admin and user 
def logout_page(request):    
    logout(request)
    return redirect('homepage')

 



#  Change Password 
@login_required(login_url='/home')
def change_password(request):    

    context = {}

    if request.method=="POST":
        current = request.POST.get("cpwd")
        newpass = request.POST.get("npwd")

        user = User.objects.get(id=request.user.id)
        check = user.check_password(current)

        un = user.username

        # print(check)
        if check == True:
            user.set_password(newpass)
            user.save()

            context["msz"] = "Password Changed Successfully  !!"
            context["col"] = "alert-success"

            # login after saving password 
            user = User.objects.get(username=un)
            # user = authenticate(username=,password=newpass)
            login(request,user)
            
        else:
            context["msz"] = "Incorrecr Current Password"
            context["col"] = "alert-danger"
            
    return render(request, 'passwordchange.html', context)


#booking room page
@login_required(login_url='/user')
def book_room_page(request):
    room = Rooms.objects.all().get(id=int(request.GET['roomid']))
    return HttpResponse(render(request,'user/bookroom.html',{'room':room}))

#For booking the room
@login_required(login_url='/user')
def book_room(request):

    if request.method == "POST":
        try:
            room_id = request.POST.get('room_id')
            check_in = datetime.datetime.strptime(request.POST.get('check_in'), "%Y-%m-%d").date()
            check_out = datetime.datetime.strptime(request.POST.get('check_out'), "%Y-%m-%d").date()
            total_person = int(request.POST.get('person'))

            # Get room safely
            room = get_object_or_404(Rooms, id=room_id)

            # Check date validity
            if check_in >= check_out:
                messages.error(request, "Check-out must be after check-in")
                return redirect("homepage")

            # Check overlapping bookings (BEST WAY 🚀)
            conflict = Reservation.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in
            ).exists()

            if conflict:
                messages.warning(request, "Sorry! Room is unavailable for selected dates")
                return redirect("homepage")

            # Create reservation directly
            Reservation.objects.create(
                guest=request.user,
                room=room,
                check_in=check_in,
                check_out=check_out,
                # person=total_person
            )
           

            messages.success(request, "Booking Successful 🎉")
            return redirect("homepage")

        except ValueError:
            messages.error(request, "Invalid input values")
            return redirect("homepage")

    return HttpResponse('Access Denied')


def handler404(request):
    return render(request, '404.html', status=404)


@login_required(login_url='/staff')
def view_room(request,):
    room_id = request.GET.get('roomid')

    if not room_id:
        return redirect('staffpanel')

    room = get_object_or_404(Rooms, id=room_id)
    reservations = Reservation.objects.filter(room=room)

    return render(request, 'staff/viewroom.html', {
        'room': room,
        'reservations': reservations
    })


@login_required(login_url='/user')
def user_bookings(request):
    if request.user.is_authenticated == False:
        return redirect('userloginpage')
    user = User.objects.all().get(id=request.user.id)
    print(f"request user id ={request.user.id}")
    bookings = Reservation.objects.all().filter(guest=user)
    totalamount = 0.0

    for b in bookings:
        totalamount += b.room.price * (b.check_out - b.check_in).days
        
    if not bookings:
        messages.warning(request,"No Bookings Found")
    return HttpResponse(render(request,'user/mybookings.html',{'bookings':bookings,'totalamount':totalamount}))


    
#for showing all bookings to staff
@login_required(login_url='/staff')
def all_bookings(request):
   
    bookings = Reservation.objects.all()
    if not bookings:
        messages.warning(request,"No Bookings Found")
    return HttpResponse(render(request,'staff/allbookings.html',{'bookings':bookings}))
    


        