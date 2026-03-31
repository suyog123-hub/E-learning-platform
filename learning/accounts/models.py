from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class CustomUser(AbstractUser):
    address= models.CharField(max_length=255,null=True)
    phone_number = models.CharField(max_length=20,null=True)
    date_joined=models.DateTimeField(auto_now=True,null=True)

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='profile')
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    name = models.CharField(max_length=20,null=True)
    bio = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    dob=models.DateField(null=True, blank=True)
    address=models.CharField(max_length=200,null=True)


    def __str__(self):
        return self.user.username

class FavoriteCourse(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='favorite_courses')
    course = models.ForeignKey('core.Course', on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.course.course_title}"