from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from tracker.models import FoodRecord, ExerciseRecord , Food, User_Info_Record, UserProfile, Exercise
from django.core.exceptions import ValidationError
from datetime import date
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, FoodType
# focus
class FoodRecordForm(forms.ModelForm):
    amount = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "id": "amount"}),
        required=True,
        min_value=0,
        initial=1
    )

    class Meta:
        model = FoodRecord
        fields = ['amount']
# focus    
class ExerciseRecordForm(forms.ModelForm):
    amount = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "id": "amount"}),
        required=True,
        min_value=0,
        initial=1
    )
    
    class Meta:
        model = ExerciseRecord
        fields = ['amount']

# aom
class MenuForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['name', 'calories', 'quantity_in_grams', 'description','food_type', 'ingredients', 'user']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter name'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter calories'}),
            'quantity_in_grams': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity in grams', 'required':'False'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description'}),
        }
        food_type = forms.ModelChoiceField(queryset=FoodType.objects.all(), required=False, widget=forms.SelectMultiple(attrs={"class": 'form-control'}))
        ingredients = forms.ModelChoiceField(queryset=Food.objects.all(), required=False, widget=forms.SelectMultiple(attrs={"class": 'form-control'}))


    #ให้แคลอรีใส่ได้แค่ค่าที่ >= 0
    def clean_calories(self):
        calories = self.cleaned_data.get('calories')
        if calories <= 0:
            raise forms.ValidationError("Calories must be a positive number.")
        return calories

    #ให้กรัมใส่ได้แค่ค่าที่ >= 0
    def clean_quantity_in_grams(self):
        quantity = self.cleaned_data.get('quantity_in_grams')
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be a positive number.")
        return quantity
    

# aom
class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'calories_burned_per_min', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter name'}),
            'calories_burned_per_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter calories'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description'}),
        }
    
    #ให้ calories_burned_per_min ใส่ได้แค่ค่าที่ >= 0
    def clean_calories_burned_per_min(self):
        calories_burned_per_min = self.cleaned_data.get('calories_burned_per_min')
        if not calories_burned_per_min:
            raise forms.ValidationError("This field is required.")
        if calories_burned_per_min <= 0:
            raise forms.ValidationError("Calories burned per minute must be a positive number.")
        return calories_burned_per_min
        

# aom
class ProfileForm(forms.ModelForm):
    firstname = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your firstname . . .",
            "id": "firstname"
        }),
        required=True
    )
    lastname = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your lastname . . .",
            "id": "lastname"
        }),
        required=True
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your username . . .",
            "id": "username"
        }),
        required=True
    )
    email = forms.EmailField(
        max_length=150,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your email . . .",
            "id": "email"
        }),
        required=True
    )
    old_password = forms.CharField(
        max_length=150,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your current password . . .",
            "id": "old_password"
        }),
        required=False
    )
    password1 = forms.CharField(
        max_length=150,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your new password . . .",
            "id": "password1"
        }),
        required=False
    )
    password2 = forms.CharField(
        max_length=150,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm your new password . . .",
            "id": "password2"
        }),
        required=False
    )
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "class": "form-control", 
            "type": "date", 
            "id": "birth_date"
        }),
        required=True
    )
    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control", 
            "id": "gender"
        }),
        required=True
    )
    goal_weight = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            "class": "form-control", 
            "id": "goal_weight",
            "placeholder": "Please enter a numeric value . . .", 
            "step": "0.01"
        }),
        required=True,
        min_value=0
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'firstname', 'lastname', 
                'birth_date', 'gender', 'goal_weight', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        user_instance = kwargs.pop('user_instance', None)
        profile_instance = kwargs.pop('profile_instance', None)
        super().__init__(*args, **kwargs)

        if user_instance and isinstance(user_instance, User):
            self.initial['username'] = user_instance.username
            self.initial['email'] = user_instance.email
            self.initial['firstname'] = user_instance.first_name
            self.initial['lastname'] = user_instance.last_name

        if profile_instance and isinstance(profile_instance, UserProfile):
            self.initial['goal_weight'] = profile_instance.goal_weight
            self.initial['gender'] = profile_instance.gender
            self.initial['birth_date'] = profile_instance.birth_date

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Check if new passwords match
        if password1 and password1 != password2:
            raise forms.ValidationError("New passwords do not match.")

        # Check old password is correct (if provided)
        if old_password and not self.instance.check_password(old_password):
            raise forms.ValidationError("Old password is incorrect.")

        # Check if username exists (excluding current user)
        username = cleaned_data.get("username")
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("A user with that username already exists.")

        # Check if email exists (excluding current user)
        email = cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("A user with that email already exists.")

        return cleaned_data

# aom
class WeightForm(forms.ModelForm):
    weight = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            "class": "form-control", 
            "id": "weight", 
            "placeholder": "Please enter a numeric value . . ."}),
        required=True,
        min_value=0
    )
    class Meta:
        model = User_Info_Record
        fields = ['weight']

# aom
class ExerForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['name', 'calories', 'quantity_in_grams', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter name'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter calories'}),
            'quantity_in_grams': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity in grams'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description'}),
            'food_type': forms.SelectMultiple(attrs={'class': 'form-control','required':'False'}),  # Multiple ingredient selection
            'ingredients': forms.SelectMultiple(attrs={'class': 'form-control','required':'False'}),  # Multiple ingredient selection
        }
        
    # def clean_calories(self):
    #     calories = self.cleaned_data.get('calories')
    #     if calories < 0:
    #         raise ValidationError('Calories must be a positive number.')
    #     return calories
    def clean(self):
            cleaned_data = super().clean()
            food_type = cleaned_data.get('food_type')
            ingredients = cleaned_data.get('ingredients')

            return cleaned_data

# focus
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Old Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')

        # ตรวจสอบความตรงกันของรหัสผ่านใหม่
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The two password fields didn’t match.")
        
        return new_password2