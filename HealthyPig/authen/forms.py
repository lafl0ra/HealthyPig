from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from tracker.models import UserProfile, User_Info_Record
from django.core.exceptions import ValidationError
from datetime import date

class RegisterForm(UserCreationForm):
    ACTIVITY_CHOICES = [  # เพื่อเอาไปคำนวน TDEE
        ('sedentary', '0% - 20% : Sedentary (little or no exercise)'),
        ('light', '20% - 40% : Lightly active (light exercise/sports 1-3 days/week)'),
        ('moderate', '40% - 60% : Moderately active (moderate exercise/sports 3-5 days/week)'),
        ('active', '60% - 80% : Active (hard exercise/sports 6-7 days a week)'),
        ('very_active', '80% - 100% : Very active (very hard exercise & a physical job)'),
    ]

    GOAL_WEIGHT_PER_WEEK_CHOICES = [
        ('easy', 'Lose 0.25 kg per week'),
        ('recommend', 'Lose 0.33 kg per week (recommend)'),
        ('normal', 'Lose 0.5 kg per week'),
        ('hard', 'Lose 1 kg per week'),
    ]
    
    # New fields for first name and last name
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your first name . . .",
            "id": "first_name"
        }),
        required=True
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your last name . . .",
            "id": "last_name"
        }),
        required=True
    )

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Create your username . . .",
            "id": "username"
        }),
        required=True
    )
    
    email = forms.EmailField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your email . . .",
            "id": "email"
        }),
        required=True
    )
    
    password1 = forms.CharField(
        max_length=150,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "id": "password1"
        }),
        required=True
    )

    password2 = forms.CharField(
        max_length=150,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "id": "password2"
        }),
        required=True
    )

    goal_weight_per_week = forms.ChoiceField(
        choices=GOAL_WEIGHT_PER_WEEK_CHOICES,
        widget=forms.Select(attrs={"class": "dropdown-item", "id": "goal_weight_per_week"}),
        required=True
    )
    
    birth_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date", "id": "birth_date"}),
        required=True
    )
    
    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        # Use Select widget for choices
        widget=forms.Select(attrs={"class": "dropdown-item", "id": "gender"}),
        required=True
    )
    
    height = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
                                 "class": "form-control", "id": "height", "placeholder": "Please enter a numeric value. . . ."}),
        required=True,
        min_value=0
    )
    
    weight = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
                                 "class": "form-control", "id": "weight", "placeholder": "Please enter a numeric value . . ."}),
        required=True,
        min_value=0
    )
    
    goal_weight = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "id": "goal_weight",
                                 "placeholder": "Please enter a numeric value . . .", "step": "0.01"}),
        required=True,
        min_value=0
    )
    
    activity = forms.ChoiceField(
        choices=ACTIVITY_CHOICES,
        widget=forms.Select(attrs={"class": "dropdown-item", "id": "activity"}),
        required=True
    )
        
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2',
                  'birth_date', 'gender', 'height', 'weight', 'goal_weight', 'activity', 'goal_weight_per_week']

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get("birth_date")
        if birth_date > date.today():
            raise ValidationError("birth date cannot be future")
        return birth_date

    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height < 50 or height > 300:
            raise ValidationError("Please enter a realistic height (cm).")
        return height

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight < 10 or weight > 300:
            raise ValidationError("Please enter a realistic weight (kg).")
        return weight
    
    def clean_goal_weight(self):
        goal_weight = self.cleaned_data.get("goal_weight")
        weight = self.cleaned_data.get("weight")

        if goal_weight <= 0:
            raise ValidationError("Goal weight must be a positive value.")

        if weight and goal_weight >= weight:
            raise ValidationError("Goal weight must be less than your current weight.")

        return goal_weight
    