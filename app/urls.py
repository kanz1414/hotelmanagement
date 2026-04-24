from django.urls import path
from . import views

urlpatterns = [

    # AUTH
    path('login/', views.staff_login, name="staff_login"),
    path('signup/', views.staff_sign_up, name="staff_signup"),

    # DASHBOARD
    path('panel/', views.panel, name="staff_panel"),

    # ROOMS
    path('add-room/', views.add_new_room, name="addroom"),
    path('edit-room', views.edit_room, name="editroom"),
    path('delete-room/<int:id>/', views.delete_room, name="delete_room"),
    path('room/<int:id>/', views.view_room, name="viewroom"),

    # LOCATION
    path('add-location/', views.add_new_location, name="addnewlocation"),

    # BOOKINGS
    path('bookings/', views.all_bookings, name="all_bookings"),

    # USERS
    path('customers/', views.customers, name="customers"),
    path('staffs/', views.staffs, name="staffs"),
    path('update-status/<int:id>/', views.update_status, name='activate_user'),
]