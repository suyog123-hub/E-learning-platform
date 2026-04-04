from django.shortcuts import render,redirect,get_list_or_404, get_object_or_404
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from accounts.models import CustomUser
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import views as auth_views
from .forms import profileForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required

import uuid
import json 
import hmac
import hashlib
import base64
from .models import FavoriteCourse


from core.models import *
# Create your views here.
def renew_password(request):
    form= PasswordChangeForm(request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"password changed successfully")
            return redirect("signin")
        else:
            for error in form.errors.values():
                messages.error(request,error)
    return render(request, 'renew_password.html', {'form': form})



'''
===================================
User Profile Views
===================================
'''
@login_required(login_url='signin')
def profile(request):
    user_profile,created= UserProfile.objects.get_or_create(user=request.user)
    form= profileForm(instance=user_profile)
    if request.method == 'POST':
        form= profileForm(request.POST,request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request,"profile updated successfully")
            return redirect("profile")
        else:
            for error in form.errors.values():
                messages.error(request,error)
    context={
        'form': form,
    }


    return render(request, 'profile.html',context)

'''
===================================
Authentication Views
===================================
'''
def signin(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']

        if not CustomUser.objects.filter(username=username).exists():
            messages.error(request,"username not found")
            return redirect("signin")

        user=authenticate(request,username=username,password=password)
        remember_me = request.POST.get('remember_me')
        if user is not None:
            login(request,user)
            if remember_me:
                request.session.set_expiry(1209600) # 2 weeks
            else:
                request.session.set_expiry(0) # expire on browser close
            messages.success(request,"logged in successfully")
            return redirect("home")
        else:
            messages.error(request,"invalid credentials")
            return redirect("signin")
    return render(request, 'signin.html')

def signout(request):
    logout(request)
    messages.success(request,"logged out successfully")
    return redirect("signin")

def register(request):
    if request.method == 'POST':
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email=request.POST['email']
        username=request.POST['username']
        phone_number=request.POST['phone_number']
        password=request.POST['password']
        password1=request.POST['password1']

        if password == password1:
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request,"username alreadt exist")
                return redirect("register")
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request,"email alreadt exist")
                return redirect("register")
            try:
                validate_password(password)
                CustomUser.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,phone_number=phone_number,password=password)
                messages.success(request,"account created successafully")
                return redirect("signin")
            except ValidationError as e:
                for i in e.messages:
                    messages.error(request,i)
                    return redirect("register")
        else:
            messages.error(request,"password doesnt match")
            return redirect('register')
    return render(request, 'register.html')

"""
================
add to cart 
================
"""
def cart(request):
    return render(request,'cart.html')

@login_required(login_url="signin")
def cart_add(request, id):
    cart = Cart(request)
    product = Course.objects.get(id=id)
    cart.add(product=product)
    return redirect('course_detail', id=product.id)


@login_required(login_url="signin")
def item_clear(request, id):
    cart = Cart(request)
    product = Course.objects.get(id=id)
    cart.remove(product)
    return redirect("cart_detail")


@login_required(login_url="signin")
def item_increment(request, id):
    cart = Cart(request)
    product = Course.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="signin")
def item_decrement(request, id):
    cart = Cart(request)
    product = Course.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")


@login_required(login_url="signin")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")

def generate_signature(data, secret):
    # signed_field_names must be included in the payload
    signed_fields = data["signed_field_names"].split(",")
    # Create message string in exact order
    message = ",".join([f"{field}={data[field]}" for field in signed_fields])
    signature = hmac.new(
    secret.encode("utf-8"),
    message.encode("utf-8"),
    hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode("utf-8")

@login_required(login_url="signin")
def cart_detail(request):
    cart=request.session.get('cart')
    amount=0
    for item in cart.values():
        amount+=item['quantity']*float(item['price'])
    amount=round(amount,2)
    tax_amount=round(amount*0.13,2)
    total_amount=round(amount+tax_amount,2)
    secret_key = "8gBm/:&EnhH.1/q"
    data = {
        "amount": amount,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
        "transaction_uuid": str(uuid.uuid4()),
        "product_code": 'EPAYTEST',
        "product_service_charge": 0,
        "product_delivery_charge": 0,
        "success_url": "http://127.0.0.1:8000/esewa/success/",
        "failure_url": "http://127.0.0.1:8000/esewa/failure/",
        "signed_field_names": "total_amount,transaction_uuid,product_code"
    }
    data['signature']=generate_signature(data,secret_key)
    return render(request, 'cart.html',data)


from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile, FavoriteCourse
from core.models import Course

@login_required(login_url="signin")
def add_to_favorites(request, course_id):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    course = get_object_or_404(Course, id=course_id)

    favorite, created = FavoriteCourse.objects.get_or_create(user=user_profile, course=course)
    if created:
        messages.success(request, "Course added to favorites.")
    else:
        messages.info(request, "Course is already in favorites.")

    return redirect('course_detail', id=course_id)  # make sure 'course_detail' exists

@login_required(login_url="signin")
def remove_from_favorites(request, course_id):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    course = get_object_or_404(Course, id=course_id)

    deleted, _ = FavoriteCourse.objects.filter(user=user_profile,course=course).delete()
    if deleted:
        messages.success(request, "Course removed from favorites.")
    else:
        messages.info(request, "Course was not in favorites.")

    return redirect('course_detail', id=course_id)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile, FavoriteCourse

@login_required(login_url="signin")
def favorites_list(request):
    # Get the UserProfile of the logged-in user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Query all favorite courses of this user
    favorite_courses = FavoriteCourse.objects.filter(user=user_profile).select_related('course', 'course__category', 'course__level1')
    
    context = {
        'favorite_courses': favorite_courses
    }
    return render(request, 'profile.html', context)