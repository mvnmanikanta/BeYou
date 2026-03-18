# store/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import random

from django.db.models import Q

from .product import (
    Product, Review, Variants, Order, OrderItem, Contact, Profile, Images, Size
)
from .category import Category
from .cart import Cart
from .utils import (
    calculate_total_amount, calculate_discount, calculate_shipping_cost, calculate_pre_tax_total
)


# =================== HOME ===================
def home(request):
    products_newdrops = Product.objects.all().order_by('id')[5:9]
    products_sesion = Product.objects.all().order_by('?')[:4]
    return render(request, 'home.html', {
        'products_newdrops': products_newdrops,
        'products_sesion': products_sesion
    })


# =================== SEARCH ===================
def search_products(request):
    query = request.GET.get('q')
    products = []

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(desciption__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

    context = {
        'products': products,
        'query': query
    }

    return render(request, 'search.html', context)


# =================== PROFILE ===================
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})


# =================== PRODUCT LIST ===================
def product(request):
    categories = Category.objects.all()
    categoryID = request.GET.get('category')
    products = Product.get_category_id(categoryID) if categoryID else Product.objects.all()
    return render(request, 'product.html', {'products': products, 'categories': categories})


# =================== PRODUCT DETAIL (SIZE-ONLY) ===================
def productdetail(request, id):
    product = get_object_or_404(Product, id=id)
    images = product.images.all()

    ctx = {'product': product, 'images': images}

    size_chart = None
    category_name = product.category.name.lower()

    if 'shirt' in category_name or 't-shirt' in category_name or 'tshirt' in category_name:
        size_chart = 'Images/Topwear.png'
    elif 'pant' in category_name or 'jean' in category_name or 'trouser' in category_name or 'short' in category_name:
        size_chart = 'Images/Bottomwear.png'

    ctx['size_chart'] = size_chart

    if getattr(product, "variant", None) != "None":
        variants_qs = Variants.objects.filter(product_id=id)

        if variants_qs.exists():
            sizes = [
                {
                    "size": v.size,
                    "stock": v.quantity
                }
                for v in variants_qs
            ]
            ctx.update({'sizes': sizes})
        else:
            ctx['no_variants_available'] = True

    return render(request, 'view.html', ctx)


# =================== AJAX: FIND VARIANT (SIZE-ONLY) ===================
def find_variant(request):
    product_id = request.GET.get('product_id')
    size_code = request.GET.get('size_id')

    if not product_id or not size_code:
        return JsonResponse({"variant_id": None, "image_urls": []})

    variant = Variants.objects.filter(
        product_id=product_id,
        size=size_code,
        is_available=True,
        quantity__gt=0
    ).order_by('id').first()

    image_urls = []
    if variant and variant.image_id:
        try:
            vimg = Images.objects.get(id=variant.image_id)
            if vimg.image:
                image_urls.append(vimg.image.url)
        except Images.DoesNotExist:
            pass

    return JsonResponse({
        "variant_id": variant.id if variant else None,
        "image_urls": image_urls
    })


# =================== ADD TO CART (SIZE/VARIANT-AWARE) ===================
@login_required
def addtocart(request):
    if request.method != 'POST':
        return redirect('product')

    product_id = request.POST.get('product_id')
    if not product_id:
        messages.error(request, "Product not specified.")
        return redirect('product')

    product = get_object_or_404(Product, id=product_id)
    variant_id = request.POST.get('variant_id')
    size = request.POST.get('size')

    variant_obj = None

    if getattr(product, "variant", None) != "None":
        if variant_id:
            variant_obj = get_object_or_404(
                Variants,
                id=variant_id,
                product_id=product_id,
                is_available=True
            )
            if not size:
                size = getattr(variant_obj, 'size', None)
        else:
            if not size:
                messages.error(request, "Please select a size before adding to cart.")
                return redirect('productdetail', id=product_id)

            variant_obj = Variants.objects.filter(
                product_id=product_id,
                size=size,
                is_available=True
            ).order_by('id').first()

            if not variant_obj:
                messages.error(request, "Selected size is currently unavailable.")
                return redirect('productdetail', id=product_id)

        if variant_obj and variant_obj.quantity <= 0:
            messages.error(request, "This size is out of stock.")
            return redirect('productdetail', id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        variant=variant_obj,
        size=size,
        defaults={'quantity': 1}
    )

    if not created:
        if variant_obj and cart_item.quantity >= variant_obj.quantity:
            messages.error(request, f"Only {variant_obj.quantity} items available for size {size}.")
            return redirect('showcart')

        cart_item.quantity += 1
        cart_item.save()

    if size:
        messages.success(request, f'Added {product.name} (Size: {size}) to your cart.')
    else:
        messages.success(request, f'Added {product.name} to your cart.')

    return redirect('showcart')


# =================== CART / ORDERS / MISC ===================
@login_required
def showcart(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('product', 'variant')
    amount = sum(item.total_cost for item in cart_items)
    return render(request, "cart.html", {'cart_items': cart_items, 'amount': amount})


@login_required
def inc_quantity(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)

    if item.variant and item.quantity >= item.variant.quantity:
        messages.error(request, f"Only {item.variant.quantity} items available for size {item.size}.")
        return redirect('showcart')

    item.quantity += 1
    item.save()
    return redirect('showcart')


@login_required
def dec_quantity(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect('showcart')


@login_required
def remove_cart(request, item_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid method")
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('showcart')


@login_required
def add_review(request, product_id):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        product = get_object_or_404(Product, id=product_id)

        if Review.objects.filter(product=product, user=request.user).exists():
            return redirect('productdetail', id=product_id)

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        return redirect('productdetail', id=product_id)

    return redirect('productdetail', id=product_id)


@login_required
def remove_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('productdetail', id=review.product.id)


@login_required
def checkout(request):
    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pin_code = request.POST.get('pin_code')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method')

        total_amount = calculate_total_amount(request.user)
        discount = calculate_discount(request.user)
        shipping_cost = calculate_shipping_cost(request.user)

        pre_tax_total = total_amount - discount - shipping_cost
        savings = discount

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

        tracking_number = str(random.randint(1111111, 9999999))
        while Order.objects.filter(tracking_number=tracking_number).exists():
            tracking_number = str(random.randint(1111111, 9999999))
        order.tracking_number = tracking_number
        order.save()

        cart_items = Cart.objects.filter(user=request.user).select_related('product', 'variant')

        for item in cart_items:
            size_instance = None
            if getattr(item, 'size', None):
                size_instance = Size.objects.filter(code=item.size).first()

            variant = Variants.objects.filter(
                product=item.product,
                size=item.size
            ).first()

            if variant and item.quantity > variant.quantity:
                messages.error(request, f"Only {variant.quantity} items left for size {item.size}.")
                return redirect('showcart')

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                size=size_instance,
                image=item.product.image
            )

            if variant:
                variant.quantity -= item.quantity
                if variant.quantity <= 0:
                    variant.quantity = 0
                    variant.is_available = False
                variant.save()

            item.delete()

        return redirect('order_success')

    total_amount = calculate_total_amount(request.user)
    discount = calculate_discount(request.user)
    shipping_cost = calculate_shipping_cost(request.user)
    total_quantity = Cart.objects.filter(user=request.user).count()

    return render(request, 'checkout.html', {
        'total_amount': total_amount,
        'discount': discount,
        'shipping_cost': shipping_cost,
        'total_quantity': total_quantity,
        'pre_tax_total': total_amount - discount - shipping_cost,
        'savings': discount,
    })


def order_success(request):
    return render(request, 'order_success.html')


@login_required
def myorders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    for order in orders:
        order.pre_tax_total = order.total_amount - order.discount - order.shipping_cost
    return render(request, 'myorders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items_with_totals = [
        {
            'product': i.product,
            'size': i.size,
            'quantity': i.quantity,
            'price': i.price,
            'total': i.quantity * i.price,
        }
        for i in order.items.all()
    ]
    return render(request, 'order_detail.html', {
        'order': order,
        'items_with_totals': items_with_totals
    })


@login_required
def track_order(request):
    tracking_number = request.GET.get('tracking_number', '').strip()
    tracking_info = None
    searched = False

    if tracking_number:
        searched = True
        tracking_info = Order.objects.filter(
            tracking_number=tracking_number,
            user=request.user
        ).first()

    return render(request, 'track_order.html', {
        'tracking_info': tracking_info,
        'tracking_number': tracking_number,
        'searched': searched,
    })


def contactus(request):
    if request.method == "POST":
        contact = Contact(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject')
        )
        contact.save()
        return HttpResponse('<h1>Thanks for Contact Us</h1>')
    return render(request, 'contactus.html')


def aboutus(request):
    return render(request, 'aboutus.html')


@login_required
def userprofile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()

        if name:
            request.user.first_name = name
            request.user.save()

        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']
            profile.save()

        return redirect('profile')

    return render(request, 'userprofile.html', {'profile': profile})