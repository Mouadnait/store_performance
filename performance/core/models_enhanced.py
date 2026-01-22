"""
Core models for Store Performance Analytics.
Includes enhanced data models with audit logging, multi-store support, and role-based access.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from django.utils import timezone
import json

# ======================== User & Auth ========================

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Email is required')
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        return self.create_user(email, password, **kwargs)


# ======================== Store Management ========================

class Store(models.Model):
    """Multi-tenant store support for scalability."""
    sid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="str", alphabet="abcdefgh12345")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey('userauths.User', on_delete=models.CASCADE, related_name='owned_stores')
    
    # Contact & Location
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Stores'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


# ======================== Audit Logging ========================

class AuditLog(models.Model):
    """Track all changes for compliance and debugging."""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('login', 'Login'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    actor = models.ForeignKey('userauths.User', on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='audit_logs', null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255)
    
    # Before/after snapshots (JSON)
    before_data = models.JSONField(blank=True, null=True)
    after_data = models.JSONField(blank=True, null=True)
    
    # Details
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['actor', 'timestamp']),
            models.Index(fields=['store', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.action.upper()} {self.model_name} by {self.actor} at {self.timestamp}"


# ======================== Clients & Relationships ========================

STATUS_CHOICES = (
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
)

STATUS = (
    ('draft', 'Draft'),
    ('disabled', 'Disabled'),
    ('in_review', 'In Review'),
    ('published', 'Published'),
)

RATING = (
    (1, '★☆☆☆☆'),
    (2, '★★☆☆☆'),
    (3, '★★★☆☆'),
    (4, '★★★★☆'),
    (5, '★★★★★'),
)


def user_directory_path(instance, filename):
    return f'user_{instance.user.id}/{filename}'


class Client(models.Model):
    """Customer/client model with multi-store support."""
    lid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cli", alphabet="abcdefgh12345")
    user = models.ForeignKey('userauths.User', on_delete=models.CASCADE, related_name='clients')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='clients', null=True, blank=True)
    
    # Profile
    profile_image = models.ImageField(upload_to=user_directory_path, default='client.png', blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Address
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Features
    gpt5_enabled = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Clients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'store']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return self.full_name


# ======================== Products & Categories ========================

class Category(models.Model):
    """Product categories with multi-store support."""
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcdefgh12345")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', default='category.jpg', blank=True)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['title']
    
    def category_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')
    
    def __str__(self):
        return self.title


class Tags(models.Model):
    """Product tags for organization."""
    name = models.CharField(max_length=100, unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Product catalog with full tracking."""
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefgh12345")
    
    user = models.ForeignKey('userauths.User', on_delete=models.SET_NULL, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='products')
    
    # Details
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=user_directory_path, default='product.jpg')
    
    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text='Cost of goods sold')
    
    # Specs & Tags
    specifications = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(Tags, blank=True, related_name='products')
    
    # Inventory
    sku = ShortUUIDField(unique=True, length=4, max_length=10, alphabet="abcdefgh12345")
    stock = models.DecimalField(max_digits=12, decimal_places=0, default=0, help_text='Current stock level')
    reorder_level = models.DecimalField(max_digits=12, decimal_places=0, default=10)
    
    # Status
    product_status = models.CharField(choices=STATUS, max_length=20, default='draft')
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['store', 'product_status']),
        ]
    
    def product_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')
    
    def get_percentage(self):
        """Calculate discount percentage safely."""
        if not self.old_price or self.old_price <= 0:
            return 0
        try:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return max(0, discount)
        except (ValueError, TypeError):
            return 0
    
    def get_profit_margin(self):
        """Calculate profit margin percentage."""
        if self.price <= 0:
            return 0
        try:
            margin = ((self.price - self.cost) / self.price) * 100
            return max(0, margin)
        except (ValueError, TypeError):
            return 0
    
    def is_low_stock(self):
        """Check if product is below reorder level."""
        return self.stock <= self.reorder_level
    
    def __str__(self):
        return self.title


class ProductImages(models.Model):
    """Additional product images."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product-images/')
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Product Images'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.title}"


# ======================== Reviews ========================

class ProductReview(models.Model):
    """Product reviews and ratings."""
    user = models.ForeignKey('userauths.User', on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING, default=3)
    title = models.CharField(max_length=255, blank=True)
    review = models.TextField()
    helpful_count = models.IntegerField(default=0)
    verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Product Reviews'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user}'s review for {self.product}"


# ======================== Sales & Billing ========================

class Bill(models.Model):
    """Sales transaction tracking."""
    bid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="bil", alphabet="abcdefgh12345")
    
    # Relationships
    store_name = models.ForeignKey('userauths.User', on_delete=models.CASCADE, related_name='bills')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='bills', null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bills')
    
    # Line item details
    quantity = models.IntegerField(default=1)
    description = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Payment
    payment_method = models.CharField(
        max_length=50, 
        choices=[('cash', 'Cash'), ('card', 'Card'), ('check', 'Check'), ('other', 'Other')],
        default='cash'
    )
    is_paid = models.BooleanField(default=False)
    
    # Metadata
    date = models.DateField(auto_now_add=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Bills'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['store', 'date']),
        ]
    
    def __str__(self):
        return f"Bill {self.bid} for {self.client} on {self.date}"


# ======================== Analytics Data ========================

class DailyMetric(models.Model):
    """Aggregated daily metrics for performance and caching."""
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='daily_metrics', null=True, blank=True)
    metric_date = models.DateField(db_index=True)
    
    # Revenue
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_quantity = models.IntegerField(default=0)
    total_transactions = models.IntegerField(default=0)
    
    # Customers
    unique_customers = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    
    # Average metrics
    average_transaction_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Metadata
    computed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Daily Metrics'
        unique_together = ['store', 'metric_date']
        ordering = ['-metric_date']
    
    def __str__(self):
        return f"{self.store} - {self.metric_date}"


class Forecast(models.Model):
    """Sales forecasts computed by analytics engine."""
    METRIC_CHOICES = [
        ('revenue', 'Revenue'),
        ('quantity', 'Quantity Sold'),
        ('transactions', 'Transactions'),
    ]
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='forecasts', null=True, blank=True)
    metric = models.CharField(max_length=50, choices=METRIC_CHOICES)
    forecast_date = models.DateField(db_index=True)
    predicted_value = models.DecimalField(max_digits=15, decimal_places=2)
    confidence_lower = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    confidence_upper = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
    actual_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    mape = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text='Mean Absolute Percentage Error')
    
    computed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Forecasts'
        unique_together = ['store', 'metric', 'forecast_date']
        ordering = ['-forecast_date']
    
    def __str__(self):
        return f"{self.metric} forecast for {self.forecast_date}"


class Anomaly(models.Model):
    """Detected anomalies in sales/inventory patterns."""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='anomalies', null=True, blank=True)
    metric = models.CharField(max_length=100)
    anomaly_date = models.DateField(db_index=True)
    actual_value = models.DecimalField(max_digits=15, decimal_places=2)
    expected_value = models.DecimalField(max_digits=15, decimal_places=2)
    deviation_percent = models.DecimalField(max_digits=10, decimal_places=2)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    description = models.TextField()
    is_investigated = models.BooleanField(default=False)
    resolution = models.TextField(blank=True)
    
    detected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Anomalies'
        ordering = ['-detected_at']
    
    def __str__(self):
        return f"{self.metric} anomaly on {self.anomaly_date}"
