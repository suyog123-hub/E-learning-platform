from django.shortcuts import render,redirect,get_list_or_404, get_object_or_404, reverse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from accounts.models import CustomUser
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import profileForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
import uuid
import json 
import hmac
import hashlib
import base64
from .models import FavoriteCourse
from core.models import *
# Create your views here.
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
        'favorite_courses': FavoriteCourse.objects.filter(user=user_profile).select_related('course', 'course__category'),
        'purchased_courses': Purchase.objects.filter(user=request.user).select_related('course', 'course__category').order_by('-purchased_at'),
    }


    return render(request, 'profile.html',context)

'''
===================================
Authentication Views
===================================
'''
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
    
def signin(request):
    if request.method == 'POST':
        username=request.POST.get('username','')
        password=request.POST.get('password','')
        next_url = request.POST.get('next')

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
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect("home")
        else:
            messages.error(request,"invalid credentials")
            return redirect("signin")
    return render(request, 'signin.html')

def signout(request):
    logout(request)
    messages.success(request,"logged out successfully")
    return redirect("signin")



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
    if not product.image and product.course_image:
        product.image = product.course_image
        product.save(update_fields=['image'])
    cart.add(product=product)
    item = cart.cart.get(str(product.id))
    if item is not None:
        item['duration'] = product.total_duration or 'Flexible'
        item['lessons'] = product.curriculums.count()
        item['instructor'] = product.instructor_name or 'Expert Instructor'
        item['mark_price'] = f"${product.mark_price}" if product.mark_price else ''
        cart.save()
    messages.success(request, f'"{product.course_title}" added to your cart.')
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
    """eSewa HMAC-SHA256 signature (base64) over the signed fields."""
    fields = data["signed_field_names"].split(",")
    message = ",".join(f"{field}={data[field]}" for field in fields)
    digest = hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def _verify_esewa(data_b64, secret):
    """Decode and verify the eSewa callback. Returns the payment dict or None."""
    if not data_b64:
        return None
    try:
        # eSewa sends base64 that may contain '+', which arrives as a space.
        value = data_b64.replace(" ", "+").replace("-", "+").replace("_", "/")
        decoded = json.loads(base64.b64decode(value + "=" * (-len(value) % 4)))
    except Exception:
        import logging
        logging.getLogger("esewa").error("callback decode failed: %r", data_b64[:200])
        return None

    if decoded.get("status") != "COMPLETE":
        import logging
        logging.getLogger("esewa").warning("status=%r", decoded.get("status"))
        return None

    received = decoded.get("signature", "")
    if not received:
        import logging
        logging.getLogger("esewa").warning("no signature in callback")
        return None

    fields = decoded.get("signed_field_names", "total_amount,transaction_uuid,product_code")
    expected = generate_signature({**decoded, "signed_field_names": fields}, secret)
    if not hmac.compare_digest(expected, received):
        import logging
        logging.getLogger("esewa").warning(
            "signature mismatch: expected=%r received=%r", expected, received
        )
        return None
    return decoded


@login_required(login_url="signin")
def cart_detail(request):
    cart_items = request.session.get(settings.CART_SESSION_ID, {}) or {}
    amount = 0
    for item in cart_items.values():
        amount += int(item.get("quantity", 1)) * float(item.get("price", 0))
    amount = f"{round(amount, 2):.2f}"
    tax_amount = f"{round(float(amount) * 0.13, 2):.2f}"
    total_amount = f"{round(float(amount) + float(tax_amount), 2):.2f}"

    data = {
        "amount": amount,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
        "transaction_uuid": str(uuid.uuid4()),
        "product_code": settings.ESEWA_PRODUCT_CODE,
        "product_service_charge": 0,
        "product_delivery_charge": 0,
        "success_url": request.build_absolute_uri(reverse('esewa_success')),
        "failure_url": request.build_absolute_uri(reverse('esewa_failure')),
        "signed_field_names": "total_amount,transaction_uuid,product_code",
    }
    data['signature'] = generate_signature(data, settings.ESEWA_SECRET_KEY)
    return render(request, 'cart.html', data)


def esewa_success(request):
    payment = _verify_esewa(request.GET.get("data", ""), settings.ESEWA_SECRET_KEY)
    if payment is None:
        messages.error(request, "Could not verify the payment with eSewa.")
        return redirect('cart_detail')
    return _enroll_user(request)


def esewa_failure(request):
    payment = _verify_esewa(request.GET.get("data", ""), settings.ESEWA_SECRET_KEY)
    if payment is not None:
        return _enroll_user(request)
    messages.error(request, "Payment was unsuccessful or cancelled. Please try again.")
    return redirect('cart_detail')


def _enroll_user(request):
    cart_items = request.session.get(settings.CART_SESSION_ID, {}) or {}
    if request.user.is_authenticated:
        for course_id in cart_items:
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                continue
            Purchase.objects.get_or_create(user=request.user, course=course)

    request.session[settings.CART_SESSION_ID] = {}
    request.session.modified = True
    messages.success(request, "Payment successful! Your courses are now in your profile.")
    return redirect('home')


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
    favorite_courses = FavoriteCourse.objects.filter(user=user_profile).select_related('course', 'course__category')
    
    context = {
        'favorite_courses': favorite_courses
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
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