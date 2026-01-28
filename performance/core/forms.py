from django import forms
from django.core.validators import FileExtensionValidator, EmailValidator
from django.core.exceptions import ValidationError
from .models import Product, Bill, Client
import re

class ProductForm(forms.ModelForm):
    """Form for creating and editing products with comprehensive validation."""
    new_category = forms.CharField(
        required=False, 
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new category name',
            'maxlength': '100',
        }),
        help_text="Add a new category if yours isn't listed."
    )
    
    class Meta:
        model = Product
        fields = ['category', 'title', 'image', 'description', 'price', 'old_price', 'specifications', 'tags', 'product_status', 'status', 'in_stock', 'featured', 'digital', 'sku']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product title',
                'required': True,
                'maxlength': '255',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter product description',
                'maxlength': '5000',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': True,
            }),
            'old_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
            }),
            'specifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter product specifications',
                'maxlength': '2000',
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'tag1, tag2, tag3',
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SKU-123456',
                'maxlength': '20',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/jpg,image/gif,image/webp',
            }),
            'product_status': forms.Select(attrs={
                'class': 'form-control',
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
            'in_stock': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'digital': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
    
    def clean_title(self):
        """Validate product title."""
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 3:
            raise ValidationError('Product title must be at least 3 characters long.')
        if len(title) > 255:
            raise ValidationError('Product title cannot exceed 255 characters.')
        return title
    
    def clean_price(self):
        """Validate product price."""
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError('Price cannot be negative.')
        if price is not None and price > 999999999.99:
            raise ValidationError('Price is too large.')
        return price
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        old_price = cleaned_data.get('old_price')
        
        if price and old_price and old_price <= price:
            self.add_error('old_price', 'Old price must be greater than the current price for a valid discount.')
        
        return cleaned_data

class BillForm(forms.ModelForm):
    """Form for creating bills with validation."""
    class Meta:
        model = Bill
        fields = ['client', 'quantity', 'description', 'price', 'amount', 'total_price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2, 'maxlength': '255'}),
        }

class ClientForm(forms.ModelForm):
    """Form for creating and editing clients with email validation."""
    class Meta:
        model = Client
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'country', 'postal_code']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name',
                'maxlength': '100',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com',
                'maxlength': '100',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890',
                'maxlength': '20',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street Address',
                'maxlength': '100',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City',
                'maxlength': '100',
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country',
                'maxlength': '100',
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345',
                'maxlength': '10',
            }),
        }
    
    def clean_email(self):
        """Validate email format."""
        email = self.cleaned_data.get('email', '').strip()
        if email:
            validator = EmailValidator()
            try:
                validator(email)
            except ValidationError:
                raise ValidationError('Please enter a valid email address.')
        return email
    
    def clean_phone(self):
        """Validate phone number format."""
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            # Remove common separators for validation
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
            if not re.match(r'^\+?[0-9]{7,20}$', cleaned_phone):
                raise ValidationError('Please enter a valid phone number.')
        return phone
    
    def clean_full_name(self):
        """Validate full name."""
        name = self.cleaned_data.get('full_name', '').strip()
        if len(name) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        if len(name) > 100:
            raise ValidationError('Name cannot exceed 100 characters.')
        return name

