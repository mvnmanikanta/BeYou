# utils.py
# this is for total cart prices
from .cart import Cart
from .product import Order

def calculate_total_amount(user):
    """Calculate the total amount for the cart."""
    cart_items = Cart.objects.filter(user=user)
    return sum(item.product.price * item.quantity for item in cart_items)

def calculate_discount(user):
    """Calculate the discount for the cart."""
    # Implement your discount logic here
    # For example, a fixed 10% discount
    discount = calculate_total_amount(user) * 0.10
    #return the discount rounded to one decimal place
    return round(discount, 1)

def calculate_shipping_cost(user):
    """Calculate the shipping cost based on the total amount."""
    total_amount = calculate_total_amount(user)
    
    # Free shipping for orders over 3000, otherwise a fixed cost
    if total_amount > 3000:
        return 0.00
    else:
        return 50.00

def calculate_pre_tax_total(total_amount, discount):
    """Calculate the pre-tax total."""
    return total_amount - discount
