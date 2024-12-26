from django.shortcuts import render
from django.http import HttpResponse
from .product import Product
from .category import Category


# Create your views here.

def home(request):
    category = Category.objects.all()
    categoryID = request.GET.get('category')
    if categoryID:
        product =Product.get_category_id(categoryID)
    else:
        product = Product.objects.all()
    data = {'products':product, 'categories': category}
    return render(request,'index.html',data ) 

