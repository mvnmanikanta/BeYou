from django.shortcuts import render, redirect, get_object_or_404 #get_object_or_404 for product view
from .product import Product
from .category import Category
from .cart import Cart
from .product import Review, Variants, Order, OrderItem, Contact, Profile
from django.http import HttpResponse
from django.core.exceptions import ValidationError

# Assume these functions are defined to calculate totals
from .utils import calculate_total_amount, calculate_discount, calculate_shipping_cost, calculate_pre_tax_total

import random
from django.contrib import messages


#used in add to cart
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django import template



# Create your views here.
def home(request):
    products_newdrops = Product.objects.all().order_by('id')[5:9] # from 5-9 products
    products_sesion = Product.objects.all().order_by('?')[:4] #random 4 products

    page = 'home'
    data={ 'products_newdrops': products_newdrops,
            'products_sesion': products_sesion
    }
    return render(request, 'home.html', data)

#profile
def profile(request):
    # Retrieve the logged-in user's profile
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'profile.html', {'profile': profile})

#products
def product(request):
    categories = Category.objects.all()

    #for filtering purpose

    categoryID = request.GET.get('category')
    if categoryID:
        products = Product.get_category_id(categoryID)

    else:
        products = Product.objects.all()

    data = {'products':products, 'categories':categories}
    return render(request, 'product.html', data)


#Product view
def productdetail(request, id):
    product = get_object_or_404(Product, id=id)
    images = product.images.all()
    star_range = range(1, 6)

    if request.method == 'POST':
        size_id = request.POST.get('size')  # Get the selected size
        if size_id:
            size = get_object_or_404(Size, id=size_id)
            # Create or update the order item (you can customize this logic based on your app's needs)
            OrderItem.objects.create(
                order=get_user_order(request.user),  # Replace with logic to fetch/create an order
                product=product,
                size=size,
                quantity=1,  # Default quantity
                price=product.price,
            )
            return redirect('cart')  # Redirect to the cart page

    data = {'p': product, 'images': images, 'star_range': star_range}
    return render(request, 'view.html', data)
    
#add to cart
def addtocart(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('product')

#show cart
def showcart(request):
    user = request.user

    if not user.is_authenticated:
        return redirect('login')

#below cart_items is used for show the product in shopping cart based on the add to cart button we click
    cart_items = Cart.objects.filter(user=user)
    amount = sum(item.total_cost for item in cart_items)  # Sum of costs using total_cost property

    data = {'cart_items': cart_items, 'amount': amount}
    return render(request, "cart.html", data)

#increase quantity
def inc_quantity(request, product_id):
    item = get_object_or_404(Cart, product_id=product_id, user=request.user)
    item.quantity +=1
    item.save()
    return redirect('showcart')

# Decrease item from cart
def dec_quantity(request, product_id):
    item = get_object_or_404(Cart, product_id=product_id, user=request.user)
    if item.quantity > 1:
        item.quantity -=1
        item.save()
    return redirect('showcart')

#remove from cart
def remove_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    cart_item = get_object_or_404(Cart, product_id=product_id, user=request.user)
    cart_item.delete()
    
    return redirect('showcart')

#review
@login_required
def add_review(request, product_id):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        product = get_object_or_404(Product, id=product_id)
        
        # Check if the user has already reviewed this product
        if Review.objects.filter(product=product, user=request.user).exists():
            return redirect('productdetail', id=product_id)
        
        # Create a new review
        Review.objects.create(product=product, user=request.user, rating=rating, comment=comment)
        return redirect('productdetail', id=product_id)

#remove review
@login_required
def remove_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('productdetail', id=review.product.id)



#checkout
@login_required
def checkout(request):
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pin_code = request.POST.get('pin_code')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method')

        # Calculate totals
        total_amount = calculate_total_amount(request.user)
        discount = calculate_discount(request.user)
        shipping_cost = calculate_shipping_cost(request.user)
        
        # Calculate pre-tax total and savings
        pre_tax_total = total_amount - discount - shipping_cost
        savings = discount  # Assuming savings are equivalent to discount for simplicity
        
        # Create the order
        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            address=address,
            city=city,
            state=state,
            pin_code=pin_code,
            email=email,
            phone=phone,
            total_amount=total_amount,
            discount=discount,
            shipping_cost=shipping_cost,
            pre_tax_total=pre_tax_total,
            savings=savings,
            payment_method=payment_method
        )

        # Generate a unique tracking number
        tracking_number = str(random.randint(1111111, 9999999))
        while Order.objects.filter(tracking_number=tracking_number).exists():
            tracking_number = str(random.randint(1111111, 9999999))
        
        order.tracking_number = tracking_number
        order.save()

        # Add items to the order
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.delete()  # Remove item from cart after creating order

        return redirect('order_success')  # Redirect to a success page

    # Handle GET requests to show totals on the checkout page
    total_amount = calculate_total_amount(request.user)
    discount = calculate_discount(request.user)
    shipping_cost = calculate_shipping_cost(request.user)
    total_quantity = Cart.objects.filter(user=request.user).count()
    
    context = {
        'total_amount': total_amount,
        'discount': discount,
        'shipping_cost': shipping_cost,
        'total_quantity': total_quantity,
        'pre_tax_total': total_amount - discount - shipping_cost,
        'savings': discount,  # Display savings as discount for the context
    }
    return render(request, 'checkout.html', context)


def order_success(request):
    return render(request, 'order_success.html')

def myorders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')  # Use prefetch_related for optimization
    
    # Calculate pre_tax_total for each order
    for order in orders:
        order.pre_tax_total = order.total_amount - order.discount - order.shipping_cost
    
    return render(request, 'myorders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Prepare item details including total for each item
    items_with_totals = [
        {
            'product': item.product,
            'quantity': item.quantity,
            'price': item.price,
            'total': item.quantity * item.price  # Calculate total for each item
        } for item in order.items.all()
    ]

    return render(request, 'order_detail.html', {
        'order': order,
        'items_with_totals': items_with_totals,  # Pass the list of items with totals
    })



@login_required
def track_order(request):
    tracking_number = request.GET.get('tracking_number')
    tracking_info = None
    
    if tracking_number:
        tracking_info = Order.objects.filter(tracking_number=tracking_number).first()  # Adjust as necessary to fetch tracking info
    
    return render(request, 'track_order.html', {'tracking_info': tracking_info})


def contactus(request):
    if request.method=="POST":
        contact=Contact()
        name=request.POST.get('name')
        email=request.POST.get('email')
        subject=request.POST.get('subject')
        contact.name=name
        contact.email=email
        contact.subject=subject
        contact.save()
        return HttpResponse('<h1>Thanks for Contact Us</h1>')
    return render(request, 'contactus.html')

    
def aboutus(request):
    return render(request, 'aboutus.html')

#userprofile
@login_required
def userprofile(request):
    try:
        # Fetch the profile associated with the logged-in user
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # If the profile doesn't exist, create one
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        # Handle form submission for updating profile
        username = request.POST.get('username', request.user.username)
        email = request.POST.get('email', profile.email)

        # Check if the new username is unique
        if username != request.user.username and User.objects.filter(username=username).exists():
            messages.error(request, "The username is already taken. Please choose a different one.")
            return redirect('userprofile')  # Stay on the profile page

        # Update user and profile information
        request.user.username = username
        profile.email = email
        request.user.save()  # Save the updated username

        # Handle profile image upload
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']

        profile.save()  # Save updated profile
        messages.success(request, "Your profile has been updated successfully!")
        return redirect('profile')  # Redirect to profile page after saving

    return render(request, 'userprofile.html', {'profile': profile})