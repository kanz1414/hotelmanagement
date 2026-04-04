from django.urls import path, include
from . import views
urlpatterns = [
    
    path('', views.staff_login,name="staffloginpage"),
    # path('login', views.staff_log_sign_page,name="staffloginpage"),
    path('signup', views.staff_sign_up,name="staffsignup"),
     path('panel', views.panel,name="staffpanel"),
    path('allbookings', views.all_bookings,name="allbookigs"),
    path('edit-room', views.edit_room),
    path('delete_room/<int:id>', views.delete_room, name="delete_room"),
    path('add-new-room', views.add_new_room,name="addroom"),
    path('room_details/<int:id>', views.view_room, name="viewroom"),    
    path('add-new-location', views.add_new_location,name="addnewlocation"),   
    path('edit-room', views.edit_room, name="edit"),
    path('customers',views.customers, name="customers"),
    path('staffs',views.staffs, name="staffs"),
    path('update_status/<int:id>', views.update_status, name='activate_user')
    # path('staff/panel/view-room', views.view_room),

]