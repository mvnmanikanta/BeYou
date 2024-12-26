from django.db import models
from .category import Category
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from PIL import Image



# Create your models here.

#Products
class Product(models.Model): 
    VARIANTS = (
        ('None','None'),
        ('Size','Size'),
        ('Color','Color'),
        ('Size-Color','Size-Color'),
    )
    name=models.CharField(max_length=30)
    category=models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    variant = models.CharField(max_length=10, choices = VARIANTS, default='None')
    image=models.ImageField(upload_to='img')
    desciption=models.TextField()
    price=models.IntegerField()
    status = models.IntegerField(default=0)

    #filtering products
    @staticmethod
    def get_category_id(get_id):
        if get_id:
            return Product.objects.filter(category=get_id)
        else:
            return Product.objects.all()

    def __str__(self):
        return self.name
 
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'
        

#product images
class Images(models.Model): 
    name=models.CharField(max_length=30)
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image=models.ImageField(upload_to='img')
    pid = models.IntegerField()

    def __str__(self):
        return self.name

#colors
class Color(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10, blank=True, null=True)
    
    def __str__(self):
        return self.name

    def color_tag(self):
        if self.code is not None:
            return mark_safe('<p style="background-color:{}">Color</p>'.format(self.code))
        else:
            return ""
         
#size
class Size(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10, blank=True, null=True)
    
    def __str__(self):
        return self.name

#variants
class Variants(models.Model):
    name = models.CharField(max_length=20)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    color=models.ForeignKey(Color, on_delete=models.CASCADE, blank=True, null=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE,blank=True, null=True)
    price=models.IntegerField()
    image_id=models.IntegerField(blank=True, null=True, default=0)
    quantity=models.IntegerField(default=1)
    
    def __str__(self):
        return self.name

    def image(self):
        img = Images.objects.get(id=self.image_id)
        if img.id is not None:
            varimage=img.image.url
        else:
            varimage=""
        return varimage

    def image_tag(self):
        img = Images.objects.get(id=self.image_id)
        if img.id is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(img.image.url))
        else:
            return "" 


# Order model to store order information
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
            # Add your logic to handle the return process here
            # This might include restocking items, issuing a refund, etc.
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
        elif self.product.image:  # Fallback to product image
            return self.product.image.url
        else:
            return '/static/path/to/default/image.png'  # Default image path

    def __str__(self):
        return f'{self.quantity} x {self.product.name} ({self.size})'

#Contact
class Contact(models.Model):
    name=models.CharField(max_length=200)
    email=models.EmailField()
    subject=models.TextField()

    def __str__(self):
        return self.name

#Userprofile
class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    email = models.EmailField()
    date_created = models.DateTimeField(auto_now_add=True)  # automatically set on creation
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)  # to store profile images

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the original save

        if self.profile_image:
            img_path = self.profile_image.path  # Get the image path
            img = Image.open(img_path)  # Open the image

            # Crop the image to a square (centered)
            width, height = img.size
            min_dimension = min(width, height)
            left = (width - min_dimension) // 2  # Left side to crop
            top = (height - min_dimension) // 2  # Top side to crop
            right = left + min_dimension  # Right side to crop
            bottom = top + min_dimension  # Bottom side to crop
            img = img.crop((left, top, right, bottom))  # Apply the crop

            # Resize to 130x130
            output_size = (130, 130)
            img = img.resize(output_size, Image.Resampling.LANCZOS)  # Use LANCZOS for high-quality resizing

            # Save the processed image
            img.save(img_path)  # Save the image back to the same file
