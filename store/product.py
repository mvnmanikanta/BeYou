from django.db import models
from .category import Category
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from PIL import Image

# -------------------- Product --------------------
class Product(models.Model):
    VARIANTS = (
        ('None', 'None'),
        ('Size', 'Size'),
    )
    name = models.CharField(max_length=30)
    product_code = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    variant = models.CharField(max_length=10, choices=VARIANTS, default='None')
    image = models.ImageField(upload_to='img')
    desciption = models.TextField()
    price = models.IntegerField()
    original_price = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(default=0)

    @staticmethod
    def get_category_id(get_id):
        if get_id:
            return Product.objects.filter(category=get_id)
        return Product.objects.all()
    @property
    def discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0
    def __str__(self):
        return self.name


# -------------------- Size --------------------
class Size(models.Model):
    name = models.CharField(max_length=20)  # e.g. "Medium"
    code = models.CharField(max_length=10, blank=True, null=True)  # e.g. "M"

    def __str__(self):
        return self.name


# -------------------- Images --------------------
class Images(models.Model):
    name = models.CharField(max_length=30)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='img')

    def __str__(self):
        return self.name


# -------------------- Variants (Size-Only) --------------------
class Variants(models.Model):
    SIZES_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
    ]
    name = models.CharField(max_length=20)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size = models.CharField(max_length=3, choices=SIZES_CHOICES)
    is_available = models.BooleanField(default=True)
    price = models.IntegerField()
    image_id = models.IntegerField(blank=True, null=True, default=0)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('product', 'size')
        indexes = [
            models.Index(fields=['product', 'size']),
            models.Index(fields=['product', 'is_available']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.size}"

    @property
    def is_in_stock(self):
        return bool(self.is_available and (self.quantity is None or self.quantity > 0))

    def image(self):
        try:
            img = Images.objects.get(id=self.image_id)
            return img.image.url if img and img.image else ""
        except Images.DoesNotExist:
            return ""

    def image_tag(self):
        try:
            img = Images.objects.get(id=self.image_id)
            if img and img.image:
                return mark_safe(f'<img src="{img.image.url}" height="50" />')
        except Images.DoesNotExist:
            pass
        return ""

    @classmethod
    def resolve_variant_id(cls, product_id, size_code):
        v = cls.objects.filter(
            product_id=product_id,
            size=size_code,
            is_available=True
        ).first()
        return v.id if v else None


# -------------------- Review --------------------
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'


# -------------------- Orders --------------------
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pre_tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    estimated_delivery = models.CharField(max_length=100, blank=True, null=True)
    current_location = models.CharField(max_length=255, blank=True, null=True)



    def __str__(self):
        return f'Order #{self.id} by {self.user.username}'

    def cancel_order(self):
        if self.status == 'Pending':
            self.status = 'Cancelled'
            self.save()
            return True
        return False

    def return_order(self):
        if self.status in ['Delivered', 'Shipped']:
            return True
        return False


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='img', blank=True, null=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, blank=True, null=True)

    def get_image(self):
        if self.image:
            return self.image.url
        elif self.product.image:
            return self.product.image.url
        return '/static/path/to/default/image.png'

    def __str__(self):
        return f'{self.quantity} x {self.product.name} ({self.size})'


# -------------------- Contact --------------------
class Contact(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.TextField()

    def __str__(self):
        return self.name


# -------------------- User Profile --------------------
class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    email = models.EmailField()
    date_created = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.profile_image:
            img_path = self.profile_image.path
            img = Image.open(img_path)

            # Center-crop to square
            width, height = img.size
            min_dimension = min(width, height)
            left = (width - min_dimension) // 2
            top = (height - min_dimension) // 2
            right = left + min_dimension
            bottom = top + min_dimension
            img = img.crop((left, top, right, bottom))

            # Resize to 130x130
            output_size = (130, 130)
            img = img.resize(output_size, Image.Resampling.LANCZOS)
            img.save(img_path)
