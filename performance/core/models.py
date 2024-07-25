from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User

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
    ( 1, '★☆☆☆☆'),
    ( 2, '★★☆☆☆'),
    ( 3, '★★★☆☆'),
    ( 4, '★★★★☆'),
    ( 5, '★★★★★'),
)

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Client(models.Model):
    lid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cli", alphabet="abcdefgh12345")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')

    profile_image = models.ImageField(upload_to=user_directory_path, default="client.png")
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.full_name

################################################### Category, Product, Product Images, Tags ###################################################
################################################### Category, Product, Product Images, Tags ###################################################
################################################### Category, Product, Product Images, Tags ###################################################
################################################### Category, Product, Product Images, Tags ###################################################

class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Category Title")
    image = models.ImageField(upload_to="category", default="category.jpg")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

class Tags(models.Model):
    pass

class Product (models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefgh12345")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)

    title = models.CharField(max_length=100, default="Product Title")
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = models.TextField(null=True, blank=True, default='This is a product description')

    price = models.DecimalField(max_digits=99999999999, decimal_places=2, default=0.00)
    old_price = models.DecimalField(max_digits=99999999999, decimal_places=2, default=1.00)

    specifications = models.TextField(null=True, blank=True, default='This is a product specification')
    tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, blank=True, null=True)

    stock = models.DecimalField(max_digits=99999999999, decimal_places=0, blank=True, null=True)

    product_status = models.CharField(choices=STATUS, max_length=20, default='in_review')

    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, length=4, max_length=10, default='sku', alphabet="abcdefgh12345")

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Product"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title
    
    def get_percentage(self):
        # (recent_price / old_price) * 100
        new_price = (self.price / self.old_price) * 100
        return new_price

class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Images"

################################################### Product Review, Bill ###################################################
################################################### Product Review, Bill ###################################################
################################################### Product Review, Bill ###################################################
################################################### Product Review, Bill ###################################################

class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return self.title

    def get_rating(self):
        return self.rating

class Bill(models.Model):
    store_name = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bill')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    quantity = models.IntegerField()
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)


    class Meta:
        verbose_name_plural = "create-bill"

    def __str__(self):
        return f"Bill for {self.client} on {self.date}"
