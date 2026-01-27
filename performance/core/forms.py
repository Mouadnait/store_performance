from django import forms
from .models import Product, Bill, Client

class ProductForm(forms.ModelForm):
    new_category = forms.CharField(
        required=False, 
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new category name',
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
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter product description',
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
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'tag1, tag2, tag3',
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SKU-123456',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
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
    
    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        old_price = cleaned_data.get('old_price')
        
        if price and old_price and old_price <= price:
            self.add_error('old_price', 'Old price must be greater than the current price for a valid discount.')
        
        return cleaned_data

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['client', 'quantity', 'description', 'price', 'amount', 'total_price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'country', 'postal_code']

