# store/cart.py (or wherever your Cart model is)
from django.db import models
from django.contrib.auth.models import User
from .product import Product, Variants  # ← add Variants if you have it

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # NEW: persist the selection
    variant = models.ForeignKey(Variants, null=True, blank=True, on_delete=models.SET_NULL)
    size    = models.CharField(max_length=20, null=True, blank=True)


    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        # Prevent duplicate lines for the same (product, variant, size) for a user
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product', 'variant', 'size'],
                name='uniq_user_product_variant_size'
            )
        ]

    @property
    def total_cost(self):
        return self.quantity * self.product.price
