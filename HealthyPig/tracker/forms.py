from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from tracker.models import FoodRecord, ExerciseRecord
from django.core.exceptions import ValidationError
from datetime import date

class FoodRecordForm(forms.ModelForm):
    amount = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            "class": "form-control", "id": "amount"}),
        required=True,
        min_value=0,
        initial=1
    )
    
    class Meta:
        model = FoodRecord
        fields = ['amount']
        
class ExerciseRecordForm(forms.ModelForm):
    amount = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            "class": "form-control", "id": "amount"}),
        required=True,
        min_value=0,
        initial=1
    )
    
    class Meta:
        model = ExerciseRecord
        fields = ['amount']
