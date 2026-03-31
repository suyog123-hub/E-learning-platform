from django.urls import path
from .views import *
urlpatterns = [
    path('', home, name='home'),
    path('enroll/',enroll, name='enroll'),
    path('about/', about, name='about'),
    path('courses/', courses, name='courses'),
    path('course_detail/<int:id>', course_detail, name='course_detail'),
    path('contact/', contact, name='contact'),



    
]