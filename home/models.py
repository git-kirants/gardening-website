from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db.models import Q
from django.conf import settings
from multiselectfield import MultiSelectField
from django.utils import timezone

class Service(models.Model):
    CATEGORY_CHOICES = [
        ('lawn', 'Lawn Care'),
        ('garden', 'Garden Maintenance'),
        ('landscape', 'Landscaping'),
        ('tree', 'Tree Service'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = (
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('inactive', 'Inactive'),
    )

    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in minutes")
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    location = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class ServiceReview(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['service', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.service.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.service.update_rating()

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('customer', 'Customer'),
        ('provider', 'Service Provider'),
        ('admin', 'Administrator'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15)
    bio = models.TextField(blank=True, null=True)
    service_area = models.CharField(max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # If user is a superuser, set user_type to admin
        if self.is_superuser:
            self.user_type = 'admin'
        super().save(*args, **kwargs)
    
    def is_customer(self):
        return self.user_type == 'customer'
    
    def is_provider(self):
        return self.user_type == 'provider'
    
    def is_admin(self):
        return self.user_type == 'admin'

class ProviderProfile(models.Model):
    SERVICES_CHOICES = (
        ('lawn_mowing', 'Lawn Mowing'),
        ('landscaping', 'Landscaping'),
        ('pest_control', 'Pest Control'),
        ('garden_maintenance', 'Garden Maintenance'),
        ('tree_trimming', 'Tree Trimming'),
        ('irrigation', 'Irrigation Services'),
        ('planting', 'Planting Services'),
    )

    DAYS_OF_WEEK = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provider_profile')
    business_name = models.CharField(max_length=100, blank=True, null=True)
    service_location = models.CharField(max_length=200, help_text="Cities or zip codes you serve")
    services_offered = MultiSelectField(choices=SERVICES_CHOICES)
    available_days = MultiSelectField(choices=DAYS_OF_WEEK)
    working_hours_start = models.TimeField()
    working_hours_end = models.TimeField()
    years_of_experience = models.PositiveIntegerField()
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, help_text="Hourly rate in $")
    flat_rate_services = models.TextField(blank=True, help_text="List any flat-rate services and their prices")
    portfolio = models.TextField(blank=True, help_text="Describe your past work and experience")
    references = models.TextField(blank=True, help_text="List any references or testimonials")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business_name or self.user.get_full_name()}'s Profile"

    class Meta:
        ordering = ['-created_at']

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_bookings')
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provider_bookings')
    booking_date = models.DateField()
    booking_time = models.TimeField()
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-booking_date', '-booking_time']

    def __str__(self):
        return f"{self.service.title} - {self.customer.username} - {self.booking_date}"
