from django import forms
from .models import Product, Bill, Client

class ProductForm(forms.ModelForm):
    new_category = forms.CharField(required=False, help_text="Add a new category if yours isn't listed.")
    class Meta:
        model = Product
        fields = ['category', 'title', 'image', 'description', 'price', 'old_price', 'specifications', 'tags', 'product_status', 'status', 'in_stock', 'featured', 'digital', 'sku']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'specifications': forms.Textarea(attrs={'rows': 4}),
        }

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

