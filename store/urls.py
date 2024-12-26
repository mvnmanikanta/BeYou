from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('product/', views.product, name='product'),
    path('productdetail/<int:id>/', views.productdetail, name='productdetail'),
    path('addtocart/', views.addtocart, name='addtocart'),  # Ensure this matches the form action
    path('cart/', views.showcart, name='showcart'),
    path('inc_quantity/<int:product_id>/', views.inc_quantity, name='inc_quantity'),
    path('dec_quantity/<int:product_id>/', views.dec_quantity, name='dec_quantity'),
    path('remove_cart/<int:product_id>/', views.remove_cart, name='remove_cart'),  # Ensure this matches the form action
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),
    path('remove_review/<int:review_id>/', views.remove_review, name='remove_review'),

    path('checkout/', views.checkout, name='checkout'), #check page
    path('order_success/', views.order_success, name='order_success'),
    path('myorders/', views.myorders, name='myorders'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('track_order/', views.track_order, name='track_order'),
    path('contactus/', views.contactus, name='contactus'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('userprofile/', views.userprofile, name='userprofile'),
]