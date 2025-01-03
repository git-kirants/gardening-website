from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Service, CustomUser, ProviderProfile, Booking
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field

class RegistrationForm(UserCreationForm):
    USER_TYPES = (
        ('customer', 'Customer'),
        ('provider', 'Service Provider'),
    )
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    user_type = forms.ChoiceField(choices=USER_TYPES, required=True)

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'user_type',
            'password1',
            'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'card shadow-sm p-4'
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6'),
                Column('last_name', css_class='form-group col-md-6'),
                css_class='row'
            ),
            Row(
                Column('username', css_class='form-group col-md-6'),
                Column('email', css_class='form-group col-md-6'),
                css_class='row'
            ),
            Row(
                Column('phone_number', css_class='form-group col-md-6'),
                Column('user_type', css_class='form-group col-md-6'),
                css_class='row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6'),
                Column('password2', css_class='form-group col-md-6'),
                css_class='row'
            ),
            Submit('submit', 'Register', css_class='btn btn-primary mt-3')
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.user_type = self.cleaned_data['user_type']
        
        if commit:
            user.save()
        return user

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'category', 'price', 'duration', 'location', 'image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter service title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your service'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Duration in minutes'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter service area or location'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required except image
        for field_name, field in self.fields.items():
            if field_name != 'image':
                field.required = True

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero")
        return price

    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration < 15:
            raise forms.ValidationError("Duration must be at least 15 minutes")
        return duration

class ProviderRegistrationForm(forms.ModelForm):
    SERVICES_CHOICES = [
        ('lawn_mowing', 'Lawn Mowing'),
        ('gardening', 'Gardening'),
        ('landscaping', 'Landscaping'),
        ('tree_trimming', 'Tree Trimming'),
        ('weed_control', 'Weed Control'),
        ('pest_control', 'Pest Control'),
        ('irrigation', 'Irrigation Systems'),
        ('leaf_removal', 'Leaf Removal'),
        ('fertilization', 'Fertilization'),
        ('mulching', 'Mulching'),
    ]

    business_name = forms.CharField(max_length=100, required=True)
    service_location = forms.CharField(max_length=200, required=True)
    services_offered = forms.MultipleChoiceField(
        choices=SERVICES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    available_days = forms.MultipleChoiceField(
        choices=[
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
            ('sunday', 'Sunday'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    working_hours_start = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=True)
    working_hours_end = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=True)
    years_of_experience = forms.IntegerField(min_value=0, required=True)
    hourly_rate = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    flat_rate_services = forms.CharField(widget=forms.Textarea, required=False)
    portfolio = forms.CharField(widget=forms.Textarea, required=False)
    references = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = ProviderProfile
        fields = [
            'business_name', 'service_location', 'services_offered',
            'available_days', 'working_hours_start', 'working_hours_end',
            'years_of_experience', 'hourly_rate', 'flat_rate_services',
            'portfolio', 'references'
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.services_offered = ','.join(self.cleaned_data['services_offered'])
            instance.save()
        return instance

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'name', 'phone_number']
        widgets = {
            'booking_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'booking_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone Number'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        
        if commit:
            user.save()
        return user
