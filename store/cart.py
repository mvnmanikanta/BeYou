from django.db import models
from .product import Product
from django.contrib.auth.models import User

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    @property #it shows the price of the prodduct in shopping cart 
    def total_cost(self):
        return self.quantity * self.product.price
 