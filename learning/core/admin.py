from django.contrib import admin
from .models import  Category, Level, Price, Course, skill_you_will_gain,Requriment,Curriculum
# Register your models here.
admin.site.register(Category)
admin.site.register(Level)
admin.site.register(Price)

class CourseAdmin(admin.TabularInline):
    model = skill_you_will_gain
    extra = 1

class RequrimentAdmin(admin.TabularInline):
    model = Requriment
    extra = 1

class CurriculumAdmin(admin.TabularInline):
    model = Curriculum
    extra = 1
    fields = ('title', 'video')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_title', 'category', 'mark_price', 'discount_price', 'price', 'total_duration', 'instructor_name', 'is_featuredCourse')
    inlines = [CourseAdmin,RequrimentAdmin,CurriculumAdmin]

@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'video')