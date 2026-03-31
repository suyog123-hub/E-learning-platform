from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'feedback']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'feedback': forms.Textarea(attrs={'rows': 4}),
        }