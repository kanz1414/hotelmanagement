"""hotel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

import broomk.views as views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage,name="homepage"),
    path('room_details/<int:id>', views.room_details, name='room_details'),
    path('contact', views.contactpage,name="contactpage"),
    path('login', views.user_login,name="userloginpage"),
    path('user/signup', views.user_sign_up,name="usersignup"),
    path('bookings', views.user_bookings,name="dashboard"),
    path('book-room', views.book_room_page,name="bookroompage"),
    path('user/book-room/book', views.book_room,name="bookroom"),
    # Logout
    path('logout', views.logout_page,name="logout"),
    # Change Password 
    path('changepassword', views.change_password, name ="change_password"),


    path('admin/', admin.site.urls),
    path('staff/', include('app.urls'))
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
