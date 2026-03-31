from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.db.models import Count , Avg
from django.core.paginator import Paginator
from .forms import ReviewForm
from accounts.models import UserProfile

from django.contrib import messages
from django.core.mail import send_mail
def home(request):
    feature = Course.objects.filter(is_featuredCourse=True)
    context = {
        'feature': feature,
    }
    return render(request, 'home.html', context)

def enroll(request):
    return render(request, 'enroll.html')

def about(request):
    return render(request, 'about.html')

def courses(request):
    category = Category.objects.annotate(num_of_courses=Count('course'))
    course_detail = Course.objects.all()
    subcategory_id = request.GET.get('category')
    serach = request.GET.get('search')
    
    if serach:
        course_detail=Course.objects.filter(course_title__icontains=serach)
    elif subcategory_id:
        course_detail = Course.objects.filter(category=subcategory_id)
    else:
        course_detail = Course.objects.all()

    paginator = Paginator(course_detail, 2)
    number_of_pages = request.GET.get('page')
    course_data = paginator.get_page(number_of_pages)
    context = {
        'category': category,
        'course_detail': course_detail,
        'course_data': course_data,
        'range':range(1,6),
        }
    return render(request, 'courses.html', context)

def course_detail(request, id):
    course = get_object_or_404(Course, id=id)
    reviews = course.reviews.all()
    good_review=course.reviews.filter(rating__gte=3)
    total_review=good_review.count()
    avg_review=reviews.aggregate(Avg('rating'))['rating__avg']
    form = ReviewForm()
    if request.method == 'POST':
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        form = ReviewForm(data=request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = user_profile  
            review.course = course
            review.save()
            return redirect('course_detail', id=course.id)

    context = {
        'course_detail': course,
        'form': form,
        'reviews': reviews,
        'good_review':good_review,
        'total_review':total_review,
        'range':range(1,6),
        'avg_review':round(avg_review) if avg_review else 0
    }
    return render(request, 'course-details.html', context)

def contact(request):
    if request.method == "POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        subject=request.POST.get("subject")
        message=request.POST.get("message")

        user=Contact(name=name,email=email,subject=subject,message=message)
        user.save()
        subject="Message from suyog"
        message="Thanks for leaving your contact we will contact you soon"
        from_email='ksuyog697@gmail.com'
        recipient_list=[email,'suyog697@gmail.com']
        send_mail(subject=subject,message=message,from_email=from_email,recipient_list=recipient_list,fail_silently=False)
        messages.success(request,f'hi {name} your form is submitted please check your email')
    return render(request, 'contact.html')

