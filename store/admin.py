from django.contrib import admin
from django.utils.html import format_html

from .product import Product, Images, Size, Variants, Order, OrderItem, Contact, Profile
from .category import Category
from .cart import Cart


# 🖼️ Inline to manage Product Images directly in Product admin
class ProductImageInline(admin.TabularInline):
    model = Images
    readonly_fields = ('id', 'preview')
    fields = ('id','name', 'image', 'preview')
    extra = 5

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="60" />', obj.image.url)
        return "-"
    preview.short_description = 'Preview'


# 🧩 Inline to manage Variants (Size-only)
class ProductVariantsInline(admin.TabularInline):
    model = Variants
    readonly_fields = ('image_tag', 'stock_status')
    fields = ('name', 'size', 'price', 'quantity', 'is_available', 'image_id', 'image_tag', 'stock_status')
    extra = 1
    show_change_link = True

    def stock_status(self, obj):
        ok = obj.is_in_stock
        label = "In stock" if ok else "Out of stock"
        color = "#16a34a" if ok else "#dc2626"
        return format_html('<b style="color:{}">{}</b>', color, label)
    stock_status.short_description = "Stock"


# 📦 Product Admin
class Productinfo(admin.ModelAdmin):
    list_display = ["name", "category", "original_price", "price", "variant", "image_preview", "variant_count"]
    inlines = [ProductImageInline, ProductVariantsInline]
    search_fields = ("name",)
    list_filter = ("category", "variant")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="50" />', obj.image.url)
        return "-"
    image_preview.short_description = "Image"

    def variant_count(self, obj):
        return obj.variants.count()
    variant_count.short_description = "Variants"


# 🏷️ Category Admin
class Categoryinfo(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ("name",)


# 🛒 Cart Admin
class Cartinfo(admin.ModelAdmin):
    list_display = ["user", "product", "quantity"]
    search_fields = ("user__username", "product__name")


# 🖼️ Images Admin
class Imagesinfo(admin.ModelAdmin):
    list_display = ["product", "id", "name", "image_preview"]
    search_fields = ("product__name", "name")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="50" />', obj.image.url)
        return "-"
    image_preview.short_description = "Preview"


# 📏 Size Admin
class Sizeinfo(admin.ModelAdmin):
    list_display = ["name", "code"]
    search_fields = ("name", "code")


# 🧩 Variants Admin (Size-only)
class Variantsinfo(admin.ModelAdmin):
    list_display = ["name", "product", "size", "price", "quantity", "is_available", "image_tag", "stock_status"]
    list_filter = ("product", "size", "is_available")
    search_fields = ("product__name", "name")
    list_editable = ("price", "quantity", "is_available")
    autocomplete_fields = ("product",)
    list_select_related = ("product",)

    def stock_status(self, obj):
        ok = obj.is_in_stock
        label = "In stock" if ok else "Out of stock"
        color = "#16a34a" if ok else "#dc2626"
        return format_html('<b style="color:{}">{}</b>', color, label)
    stock_status.short_description = "Stock"


# 🧾 Order Items Inline (inside Order Admin)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False

    fields = ('product', 'display_product_code', 'size', 'quantity', 'price', 'display_image')
    readonly_fields = ('product', 'display_product_code', 'size', 'quantity', 'price', 'display_image')

    def display_product_code(self, obj):
        if obj.product and obj.product.product_code:
            return obj.product.product_code
        return "-"
    display_product_code.short_description = "Product Code"

    def display_image(self, obj):
        img_url = obj.get_image()
        if img_url:
            return format_html('<img src="{}" height="50" />', img_url)
        return "-"
    display_image.short_description = 'Image'

# 📦 Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'created_at', 'status', 'tracking_number', 'current_location', 'estimated_delivery')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('user__username', 'tracking_number')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)


# 📬 Contact Admin
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')


# 👤 Profile Admin
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'date_created')
    search_fields = ('user__username', 'email')


# 📝 Register all models
admin.site.register(Product, Productinfo)
admin.site.register(Category, Categoryinfo)
admin.site.register(Images, Imagesinfo)
admin.site.register(Cart, Cartinfo)
admin.site.register(Size, Sizeinfo)
admin.site.register(Variants, Variantsinfo)
admin.site.register(Order, OrderAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Profile, ProfileAdmin)
