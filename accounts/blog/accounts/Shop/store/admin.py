from django.contrib import admin
from .product import Product
from .category import Category

class Categoryinfo(admin.ModelAdmin):
    list_display=["name"]
class Productinfo(admin.ModelAdmin):
    list_display =["name","category","price","image"]
# Register your models here.

admin.site.register(Product, Productinfo )
admin.site.register(Category, Categoryinfo)
