urlpatterns = [
    path('', views.homepage, name="home"),
    path('login/', views.user_login, name="login"),
    path('signup/', views.user_signup, name="signup"),
    path('logout/', views.logout_page, name="logout"),
    path('room/<int:id>/', views.room_details, name="room_details"),
    path('book/', views.book_room_page, name="bookroompage"),
    path('book-room/', views.book_room, name="book_room"),
    path('contact/', views.contactpage, name="contact"),
    path('dashboard/', views.user_dashboard, name="dashboard"), 
    path('admin/', admin.site.urls),
    path('booking-confirmation/<int:id>/', views.booking_confirmation, name="confirmation"),
    path('staff/', include('app.urls'))
]

# ✅ THIS MUST BE ON NEW LINE
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)