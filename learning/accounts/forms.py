from django import forms
from .models import CustomUser, UserProfile

class profileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image','name','bio','dob','address']

        widgets = {
            'dob':forms.DateInput(attrs={'type':'date'}),

        }


