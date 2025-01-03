from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm, ServiceForm, ProviderRegistrationForm, BookingForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from .models import Service, ProviderProfile, Booking
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import PermissionDenied

# Helper function to check if user is a provider
def is_provider(user):
    return user.is_authenticated and user.is_provider()

def home_view(request):
    context = {
        'is_provider': request.user.is_authenticated and request.user.is_provider(),
    }
    return render(request, 'home/home.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'customer'  # Set user_type for regular registration
            user.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'home/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home page after successful login
    else:
        form = AuthenticationForm()
    return render(request, 'home/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to home page after logout

@login_required
def create_service(request):
    if not hasattr(request.user, 'is_provider') or not request.user.is_provider:
        messages.error(request, "Only service providers can create services.")
        return redirect('home')

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.status = 'available'  # Set default status
            service.save()
            messages.success(request, 'Service created successfully!')
            return redirect('my_services')
    else:
        form = ServiceForm()

    return render(request, 'home/create_service.html', {
        'form': form,
        'title': 'Create New Service'
    })

def browse_services(request):
    # Get the search query from GET parameters
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    # Start with all services
    services = Service.objects.select_related('provider').order_by('-created_at')
    
    # Apply search filter if query exists
    if query:
        services = services.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )
    
    # Apply category filter if selected
    if category:
        services = services.filter(category=category)

    # Get unique categories for the filter dropdown
    categories = Service.CATEGORY_CHOICES

    context = {
        'services': services,
        'categories': categories,
        'current_category': category,
        'search_query': query
    }
    
    return render(request, 'home/browse_services.html', context)

@login_required
def my_services(request):
    if not hasattr(request.user, 'is_provider') or not request.user.is_provider:
        messages.error(request, "Only service providers can view their services.")
        return redirect('home')
        
    services = Service.objects.filter(provider=request.user).order_by('-created_at')
    return render(request, 'home/my_services.html', {'services': services})

@login_required
def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    context = {
        'service': service,
        'is_owner': request.user == service.provider
    }
    return render(request, 'home/service_detail.html', context)

@login_required
def delete_service(request, slug):
    service = get_object_or_404(Service, slug=slug, provider=request.user)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully!')
        return redirect('my_services')
    return redirect('service_detail', slug=slug)

@login_required
def register_provider(request):
    # Check if user is already a provider
    if request.user.is_provider():
        messages.warning(request, "You are already registered as a provider.")
        return redirect('home')

    if request.method == 'POST':
        form = ProviderRegistrationForm(request.POST)
        if form.is_valid():
            # Update user type
            request.user.user_type = 'provider'
            request.user.save()
            
            # Create provider profile
            provider_profile = form.save(commit=False)
            provider_profile.user = request.user
            provider_profile.is_available = True
            provider_profile.save()
            
            messages.success(request, 'Successfully registered as a provider!')
            return redirect('home')
    else:
        form = ProviderRegistrationForm()
    
    return render(request, 'home/register_provider.html', {'form': form})

def provider_list(request):
    providers = ProviderProfile.objects.select_related('user').all()
    return render(request, 'home/provider_list.html', {'providers': providers})

@login_required
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    
    # Check if user has permission to edit
    if not request.user.is_authenticated or \
       request.user.user_type != 'provider' or \
       request.user != service.provider:
        raise PermissionDenied("You don't have permission to edit this service.")
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            service = form.save()
            return redirect('service_detail', slug=service.slug)
    else:
        form = ServiceForm(instance=service)
    return render(request, 'home/service_update.html', {'form': form, 'service': service})

@login_required
def create_booking(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    # Prevent booking your own service
    if request.user == service.provider:
        messages.error(request, "You cannot book your own service.")
        return redirect('service_detail', slug=service.slug)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.service = service
            booking.customer = request.user
            booking.provider = service.provider
            booking.status = 'pending'
            booking.save()
            
            messages.success(request, 'Booking request sent successfully!')
            return redirect('customer_bookings')
    else:
        # Pre-fill the form with user's information if available
        initial_data = {}
        if hasattr(request.user, 'get_full_name'):
            initial_data['name'] = request.user.get_full_name()
        form = BookingForm(initial=initial_data)
    
    return render(request, 'home/booking_form.html', {
        'form': form,
        'service': service
    })

@login_required
def customer_bookings(request):
    try:
        # Debug information
        print(f"User: {request.user.username}")
        print(f"Is authenticated: {request.user.is_authenticated}")
        print(f"Is provider: {getattr(request.user, 'is_provider', False)}")

        # Get all bookings for the current user
        bookings = Booking.objects.filter(
            customer=request.user
        ).select_related(
            'service',
            'service__provider',
            'customer'
        ).order_by('-booking_date', '-booking_time')

        print(f"Number of bookings found: {bookings.count()}")
        for booking in bookings:
            print(f"Booking: {booking.service.title} - {booking.status}")

        context = {
            'bookings': bookings,
            'user_type': 'customer'
        }
        
        return render(request, 'home/customer_bookings.html', context)
    
    except Exception as e:
        print(f"Error in customer_bookings view: {str(e)}")
        messages.error(request, "An error occurred while loading your bookings.")
        return redirect('home')

@login_required
def my_bookings(request):
    if not (hasattr(request.user, 'is_provider') and request.user.is_provider):
        messages.error(request, "This page is for providers only.")
        return redirect('home')
    
    bookings = Booking.objects.filter(
        service__provider=request.user
    ).select_related(
        'service', 
        'customer'
    ).order_by('-booking_date', '-booking_time')

    context = {
        'bookings': bookings,
    }
    return render(request, 'home/my_bookings.html', context)

@login_required
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Customer actions
        if request.user == booking.customer:
            if action == 'cancel' and booking.status in ['pending', 'accepted']:
                booking.status = 'cancelled'
                booking.save()
                messages.success(request, 'Booking cancelled successfully!')
                return redirect('customer_bookings')
        
        # Provider actions
        elif request.user == booking.service.provider:
            if action == 'accept' and booking.status == 'pending':
                booking.status = 'accepted'
                messages.success(request, 'Booking accepted successfully!')
            elif action == 'reject' and booking.status == 'pending':
                booking.status = 'rejected'
                messages.success(request, 'Booking rejected successfully!')
            elif action == 'complete' and booking.status == 'accepted':
                booking.status = 'completed'
                messages.success(request, 'Booking marked as completed!')
            booking.save()
            return redirect('my_bookings')
    
    messages.error(request, "Invalid action or insufficient permissions.")
    return redirect('home')