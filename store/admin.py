from django.contrib import admin

from .product import Product, Images, Color, Size, Variants, Order, OrderItem, Contact, Profile
from .category import Category
from .cart import Cart


# Register your models here.

#show the products and images in admin pannel in products we can change modifications
class ProductImageInline(admin.TabularInline):
    model = Images
    readonly_fields = ('id',)
    extra = 5
    
class ProductVariantsInline(admin.TabularInline):
    model = Variants
    readonly_fields = ('image_tag',)
    extra = 1
    show_change_link = True


class Productinfo(admin.ModelAdmin):
    list_display = ["name","category","price","image"]
    inlines = [ProductImageInline, ProductVariantsInline] #access ProductImageInline, ProductVariantsInline here
 
 
class Categoryinfo(admin.ModelAdmin):
    list_display = ["name"]

class Cartinfo(admin.ModelAdmin):
    list_display = ["user","product","quantity"]

class Imagesinfo(admin.ModelAdmin):
    list_display = ["name", "image"]


class Colorinfo(admin.ModelAdmin):
    list_display = ["name", "code","color_tag"]

class Sizeinfo(admin.ModelAdmin):
    list_display = ["name", "code"]

class Variantsinfo(admin.ModelAdmin):
    list_display = ["name","product","color","size","price","quantity","image_tag"]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('price', 'display_image')
    extra = 1
    fields = ('product', 'quantity', 'price', 'display_image')  # Use 'display_image' instead of 'get_image'

    def display_image(self, obj):
        return f'<img src="{obj.get_image()}" height="50" />'
    display_image.allow_tags = True
    display_image.short_description = 'Image'  # Descriptive name in the admin panel

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'created_at', 'status')
    list_filter = ('status', 'created_at', 'user')  # Filters for the admin interface
    search_fields = ('user__username', 'tracking_number')  # Enables search by username or tracking number
    inlines = [OrderItemInline]


admin.site.register(Product, Productinfo)
admin.site.register(Category, Categoryinfo)
admin.site.register(Images, Imagesinfo)
admin.site.register(Cart, Cartinfo)
admin.site.register(Color, Colorinfo)
admin.site.register(Size,Sizeinfo)
admin.site.register(Variants, Variantsinfo)
admin.site.register(Order, OrderAdmin)
admin.site.register(Contact)#contact
admin.site.register(Profile)#Profile



