from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
import re
import random


def home(request):
    return render(request, 'index.html')


def is_valid_phone(phone):
    return bool(re.fullmatch(r'\d{10}', phone))


# Register
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phonenumber = request.POST.get('phonenumber', '').strip()
        password = request.POST.get('password', '')
        conpassword = request.POST.get('conpassword', '')

        if not name:
            messages.error(request, 'Name is required.')
            return redirect('register')

        if not phonenumber:
            messages.error(request, 'Phone number is required.')
            return redirect('register')

        if not is_valid_phone(phonenumber):
            messages.error(request, 'Phone number must be exactly 10 digits.')
            return redirect('register')

        if not password or not conpassword:
            messages.error(request, 'Password is required.')
            return redirect('register')

        if password != conpassword:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('register')

        if User.objects.filter(username=phonenumber).exists():
            messages.error(request, 'Phone number already registered.')
            return redirect('register')

        user = User.objects.create_user(
            username=phonenumber,   # phone number stays constant
            first_name=name,        # editable user name
            password=password
        )
        user.save()

        messages.success(request, 'Registered successfully.')
        return redirect('login')

    return render(request, 'register.html')


# Login
def login(request):
    if request.method == 'POST':
        phonenumber = request.POST.get('phonenumber', '').strip()
        password = request.POST.get('password', '')

        if not phonenumber:
            messages.error(request, 'Phone number is required.')
            return redirect('login')

        if not is_valid_phone(phonenumber):
            messages.error(request, 'Enter valid 10-digit phone number.')
            return redirect('login')

        if not password:
            messages.error(request, 'Password is required.')
            return redirect('login')

        user = auth.authenticate(username=phonenumber, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid phone or password.')
            return redirect('login')

    return render(request, 'login.html')


# Logout
def logout(request):
    auth.logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


# Forgot Password - Step 1
def forgot_password(request):
    if request.method == 'POST':
        phonenumber = request.POST.get('phonenumber', '').strip()

        if not phonenumber:
            messages.error(request, 'Phone number is required.')
            return redirect('forgot_password')

        if not is_valid_phone(phonenumber):
            messages.error(request, 'Phone number must be exactly 10 digits.')
            return redirect('forgot_password')

        if not User.objects.filter(username=phonenumber).exists():
            messages.error(request, 'No account found with this phone number.')
            return redirect('forgot_password')

        otp = str(random.randint(100000, 999999))

        request.session['reset_phone'] = phonenumber
        request.session['reset_otp'] = otp
        request.session['otp_verified'] = False

        print(f"Password Reset OTP for {phonenumber}: {otp}")

        messages.success(request, 'OTP generated successfully. Check terminal for now.')
        return redirect('verify_otp')

    return render(request, 'forgot_password.html')


# Forgot Password - Step 2
def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        session_otp = request.session.get('reset_otp')

        if not session_otp:
            messages.error(request, 'OTP session expired. Try again.')
            return redirect('forgot_password')

        if entered_otp == session_otp:
            request.session['otp_verified'] = True
            messages.success(request, 'OTP verified successfully.')
            return redirect('reset_password')

        messages.error(request, 'Invalid OTP.')
        return redirect('verify_otp')

    return render(request, 'verify_otp.html')


# Forgot Password - Step 3
def reset_password(request):
    phonenumber = request.session.get('reset_phone')
    otp_verified = request.session.get('otp_verified', False)

    if not phonenumber or not otp_verified:
        messages.error(request, 'Unauthorized access. Verify OTP first.')
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        conpassword = request.POST.get('conpassword', '')

        if not password or not conpassword:
            messages.error(request, 'Both password fields are required.')
            return redirect('reset_password')

        if password != conpassword:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('reset_password')

        try:
            user = User.objects.get(username=phonenumber)
            user.set_password(password)
            user.save()

            request.session.pop('reset_phone', None)
            request.session.pop('reset_otp', None)
            request.session.pop('otp_verified', None)

            messages.success(request, 'Password reset successfully. Please login.')
            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('forgot_password')

    return render(request, 'reset_password.html')