from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
# Create your views here.

def home(request):
    return render(request, 'index.html')

#Registeration
def register(request):

    if request.method == 'POST':

        username = request.POST.get('username') 
        email = request.POST.get('email') 
        password = request.POST.get('password')
        conpassword = request.POST.get('conpassword') 

        if password == conpassword:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username exists')
                return redirect('register')

            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email exists')
                return redirect('register')

            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'Registered successfully')
                return redirect('home') #login
        else:
            messages.info(request, 'paswords do not match')
            return redirect('register')
    else:
        return render(request, 'register.html')





#Login
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request,'login in successfully')
            return redirect('home')
        else:
            messages.error(request, 'Invalid user')
            return redirect('login')
    else:
        return render(request, 'login.html')


#logout
def logout(request):
    auth.logout(request)
    return redirect('home')