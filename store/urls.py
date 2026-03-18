from django.urls import path
from . import views

urlpatterns = [

    # Search
    path('search/', views.search_products, name='search_products'),

    # 🏠 HOME & PROFILE
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('userprofile/', views.userprofile, name='userprofile'),

    # 🛍️ PRODUCTS (size-only PDP supported)
    path('product/', views.product, name='product'),
    path('productdetail/<int:id>/', views.productdetail, name='productdetail'),

    # 🔄 VARIANT AJAX (size-only)
    path('find-variant/', views.find_variant, name='find_variant'),

    # 🛒 CART
    path('cart/', views.showcart, name='showcart'),
    path('cart/add/', views.addtocart, name='addtocart'),             # POST target from PDP
    path('cart/inc/<int:item_id>/', views.inc_quantity, name='inc_quantity'),
    path('cart/dec/<int:item_id>/', views.dec_quantity, name='dec_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_cart, name='remove_cart'),

    # ✍️ REVIEWS
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),
    path('remove_review/<int:review_id>/', views.remove_review, name='remove_review'),

    # 💳 CHECKOUT & ORDERS
    path('checkout/', views.checkout, name='checkout'),
    path('order_success/', views.order_success, name='order_success'),
    path('myorders/', views.myorders, name='myorders'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('track_order/', views.track_order, name='track_order'),

    # ☎️ CONTACT & INFO PAGES
    path('contactus/', views.contactus, name='contactus'),
    path('aboutus/', views.aboutus, name='aboutus'),
]
