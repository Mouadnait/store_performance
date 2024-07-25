from django import forms
from .models import Product, Bill

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
        fields = ['store_name', 'client', 'quantity', 'description', 'price', 'amount', 'total_price']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

