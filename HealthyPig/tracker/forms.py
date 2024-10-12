from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from tracker.models import FoodRecord, ExerciseRecord , Food
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


class MenuForm(forms.ModelForm):

    class Meta:
        model = Food
        fields = ['name', 'calories', 'quantity_in_grams', 'description']
        # widget=forms.NumberInput(attrs={
        #     "class": "form-control", "id": "amount"}),
        # required=True,
        # min_value=0,
        # initial=1
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter name'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter calories'}),
            'quantity_in_grams': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity_in_grams'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description'}),
        }
    # def clean_hire_date(self):

    #     hire_date = self.cleaned_data.get("hire_date")
    #     birth_date = self.cleaned_data.get("birth_date")

    #     if hire_date > date.today():
    #         raise ValidationError(
    #                 "hire date cannot be future"
    #             )
    #     if birth_date > hire_date:
    #         raise ValidationError(
    #                 "birth date cannot be future than hire date"
    #             )
    
    #     return hire_date
class FoodForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # หรือ forms.SelectMultiple สำหรับ dropdown
        required=False  # เนื่องจากคุณบอกว่าเป็น optional
    )

    class Meta:
        model = Food
        fields = ['name', 'calories', 'quantity_in_grams', 'description', 'ingredients']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter name'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter calories'}),
            'quantity_in_grams': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity in grams'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description'}),
        }