from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import *
from django.db.models import Count , Avg
from django.core.paginator import Paginator
from .forms import ReviewForm
from accounts.models import UserProfile
from django.contrib import messages
from django.core.mail import send_mail
from threading import Thread

SORT_OPTIONS = {
    'newest': '-upload_date',
    'price_low': 'price',
    'price_high': '-price',
    'duration': 'total_duration',
}

def home(request):
    feature = Course.objects.filter(is_featuredCourse=True).select_related('category')
    context = {
        'feature': feature,
    }
    return render(request, 'home.html', context)

def enroll(request):
    all_courses = Course.objects.all()
    if request.method == 'POST':
        course_id = request.POST.get('course')
        course = get_object_or_404(Course, id=course_id) if course_id else None
        if course is None:
            messages.error(request, "Please select a course to enroll in.")
            return render(request, 'enroll.html', {'courses': all_courses})

        first_name = request.POST.get('firstName', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        email = request.POST.get('email', '').strip()
        if not (first_name and last_name and email):
            messages.error(request, "First name, last name and email are required.")
            return render(request, 'enroll.html', {'courses': all_courses})

        Enrollment.objects.create(
            course=course,
            user=request.user if request.user.is_authenticated else None,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=request.POST.get('phone', '').strip(),
            education=request.POST.get('education', ''),
            experience=request.POST.get('experience', ''),
            motivation=request.POST.get('motivation', ''),
            schedule=request.POST.get('schedule', ''),
        )
        messages.success(request, f'You have been enrolled in "{course.course_title}". Check your email for details.')
        return redirect('courses')
    return render(request, 'enroll.html', {'courses': all_courses})

def about(request):
    return render(request, 'about.html')

def courses(request):
    category = Category.objects.annotate(num_of_courses=Count('course'))

    course_detail = Course.objects.select_related('category').all()

    search = request.GET.get('search')
    category_id = request.GET.get('category')
    sort = request.GET.get('sort')

    if search:
        course_detail = course_detail.filter(course_title__icontains=search)
    if category_id:
        course_detail = course_detail.filter(category=category_id)

    course_detail = course_detail.order_by(SORT_OPTIONS.get(sort, '-upload_date'))

    paginator = Paginator(course_detail, 6)
    page = request.GET.get('page')
    course_data = paginator.get_page(page)

    context = {
        'category': category,
        'course_detail': course_detail,
        'course_data': course_data,
    }
    return render(request, 'courses.html', context)

def course_detail(request, id):
    course = get_object_or_404(Course, id=id)
    is_purchased = request.user.is_authenticated and Purchase.objects.filter(user=request.user, course=course).exists()
    reviews = course.reviews.all()
    good_review = course.reviews.filter(rating__gte=3)
    total_review = good_review.count()
    avg_review = reviews.aggregate(Avg('rating'))['rating__avg']

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.info(request, "Please sign in to submit a review.")
            return redirect(f"{reverse('signin')}?next={request.path}")
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        form = ReviewForm(data=request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = user_profile
            review.course = course
            review.save()
            messages.success(request, "Your review was submitted successfully.")
            return redirect('course_detail', id=course.id)
    else:
        form = ReviewForm()

    context = {
        'course_detail': course,
        'is_purchased': is_purchased,
        'form': form,
        'reviews': reviews,
        'good_review': good_review,
        'total_review': total_review,
        'range': range(1, 6),
        'avg_review': round(avg_review) if avg_review else 0
    }
    return render(request, 'course-details.html', context)

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if not (name and email and message):
            messages.error(request, "Please fill in your name, email and message.")
            return render(request, 'contact.html')

        Contact.objects.create(name=name, email=email, subject=subject, message=message)
        from_email = settings.EMAIL_HOST_USER or 'Learner <noreply@learner.com>'
        auto_reply = "Thanks for leaving your contact. We will get back to you soon!"
        recipient_list = [email]
        try:
            thread = Thread(target=send_mail, kwargs={
                "subject": "Message from Learner",
                "message": auto_reply,
                "from_email": from_email,
                "recipient_list": recipient_list,
                "fail_silently": False,
            }, daemon=True)
            thread.start()
        except Exception:
            pass
        messages.success(request, f'Hi {name}, your form was submitted. Please check your email.')
    return render(request, 'contact.html')

