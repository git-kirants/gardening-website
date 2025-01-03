from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Service related URLs
    path('service/create/', views.create_service, name='create_service'),
    path('services/', views.browse_services, name='browse_services'),
    path('services/my-services/', views.my_services, name='my_services'),
    path('service/<slug:slug>/', views.service_detail, name='service_detail'),
    path('service/<slug:slug>/delete/', views.delete_service, name='delete_service'),
    path('service/<int:pk>/update/', views.service_update, name='service_update'),
    
    # Provider related URLs
    path('register-provider/', views.register_provider, name='register_provider'),
    path('providers/', views.provider_list, name='provider_list'),
    
    # Booking related URLs
    path('bookings/customer/', views.customer_bookings, name='customer_bookings'),
    path('bookings/provider/', views.my_bookings, name='my_bookings'),
    path('booking/<int:service_id>/create/', views.create_booking, name='create_booking'),
    path('booking/<int:booking_id>/update-status/', views.update_booking_status, name='update_booking_status'),
]