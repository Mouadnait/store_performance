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

class Category (models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="cat", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Category Title")
    image = models.ImageField(upload_to="category", default="category.jpg")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def _str_(self):
        return self.title

class Tags(models.Model):
    pass

class Vendor (models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="ven", alphabet="abcdefgh12345")

    title = models.CharField(max_length=100, default="Vendor Title")
    image = models.ImageField(upload_to=user_directory_path, default="Vendor.jpg")
    description = models.TextField(null=True, blank=True, default='This is a Vender description')

    address = models.CharField(max_length=100, default="123 Main Street")
    contact = models.CharField(max_length=100, default="+212 655 1212")
    chat_resp_time = models.CharField(max_length=100, default="100")
    chipping_on_time = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")
    days_return = models.CharField(max_length=100, default="100")
    warranty_period = models.CharField(max_length=100, default="100")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Vendor"

    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def _str_(self):
        return self.title

class Product (models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefgh12345")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=100, default="Product Title")
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = models.TextField(null=True, blank=True, default='This is a product description')

    price = models.DecimalField(max_digits=99999999999, decimal_places=2, default=0.00)
    old_price = models.DecimalField(max_digits=99999999999, decimal_places=2, default=1.99)

    specifications = models.TextField(null=True, blank=True, default='This is a product specification')
    tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True)

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

    def _str_(self):
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


################################################### Cart, Order, OrderItems And Address ###################################################
################################################### Cart, Order, OrderItems And Address ###################################################
################################################### Cart, Order, OrderItems And Address ###################################################
################################################### Cart, Order, OrderItems And Address ###################################################


class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=99999999999, decimal_places=2, default=0.00)
    paid_status = models.BooleanField(default=False)
    older_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICES, max_length=30, default='processing')

    class Meta:
        verbose_name_plural = "Cart Order"

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=99999999999, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=99999999999, decimal_places=2, default=0.00)

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_img(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image))


################################################### Product Review, Wishlists, Address ###################################################
################################################### Product Review, Wishlists, Address ###################################################
################################################### Product Review, Wishlists, Address ###################################################
################################################### Product Review, Wishlists, Address ###################################################


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def _str_(self):
        return self.product.title

    def get_rating(self):
        return self.rating

class Wishlists(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlists"

    def _str_(self):
        return self.product.title

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"

