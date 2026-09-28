from django.db import models
from accounts.models import CustomUser,UserProfile
from django.core.exceptions import ValidationError
# Create your models here.
    
class Category(models.Model):
    title=models.CharField(max_length=100)

    def __str__(self):
        return self.title
class Level(models.Model):
    title=models.CharField(max_length=50,null=True)

    def __str__(self):
        return self.title
    
class Price(models.Model):
    title=models.CharField(max_length=50,null=True)

    def __str__(self):
        return self.title
    
class Course(models.Model):
    category=models.ForeignKey(Category, on_delete=models.CASCADE,null=True)
    course_image = models.ImageField(upload_to='course_images/',null=True)
    mark_price=models.DecimalField(max_digits=8,decimal_places=2,null=True)
    discount_price=models.DecimalField(max_digits=4,decimal_places=2,null=True)
    price=models.DecimalField(max_digits=8,decimal_places=2,editable=False,null=True)
    total_duration=models.CharField(max_length=50,null=True)
    course_title=models.CharField(max_length=200,null=True)
    desc=models.TextField(null=True)
    instructor_image=models.ImageField(upload_to='instructor_images/',null=True)
    instructor_name=models.CharField(max_length=100,null=True)
    instructor_experience=models.CharField(max_length=100,null=True)
    is_featuredCourse=models.BooleanField(default=False,null=True)
    intro_video=models.FileField(upload_to='intro_videos/',null=True)
    upload_date=models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    image = models.ImageField(
        upload_to='course_images/', 
        blank=True, 
        null=True,
        verbose_name="wishlist Course Image"
    )

    @property
    def name(self):
        return self.course_title  # cart needs .name


    def save(self,*args, **kwargs):
        if self.mark_price is not None:
            discount = self.discount_price if self.discount_price is not None else 0
            self.price = self.mark_price * (1 - discount / 100)
        if not self.image and self.course_image:
            self.image = self.course_image
        super().save(*args, **kwargs)

    
    def __str__(self):
        return self.course_title
    
class skill_you_will_gain(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE,null=True,related_name='skills')
    icon=models.CharField(max_length=50,null=True)
    skill_name=models.CharField(max_length=100,null=True,blank=True)
    skill_desc=models.TextField(null=True,blank=True)

    def __str__(self):
        return self.skill_name
    
class Requriment(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE,null=True,related_name='requirements')
    requirement_name=models.CharField(max_length=200,null=True,blank=True)

    def __str__(self):
        return self.requirement_name
    
class Curriculum(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE,null=True,related_name='curriculums')
    title=models.CharField(max_length=200,null=True,blank=True)
    video=models.FileField(upload_to='curriculum_videos/',null=True,blank=True)

    def __str__(self):
        return self.title or f"Video #{self.id}"

    


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name='userprofile')
    rating = models.IntegerField(null=True)
    feedback = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)

class Contact(models.Model):
    name=models.CharField(max_length=200,null=True)
    email=models.EmailField(null=True)
    subject=models.CharField(max_length=200,null=True)
    message=models.TextField(null=True,)

class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollments', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    education = models.CharField(max_length=50, null=True, blank=True)
    experience = models.CharField(max_length=50, null=True, blank=True)
    motivation = models.TextField(null=True, blank=True)
    schedule = models.CharField(max_length=50, null=True, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.course.course_title}"

class Purchase(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='purchases')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='purchases')
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user} - {self.course.course_title}"

