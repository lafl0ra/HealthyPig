from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from tracker.models import FoodRecord, ExerciseRecord , Food, User_Info_Record, UserProfile
from django.core.exceptions import ValidationError
from datetime import date

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


class MenuForm(forms.ModelForm):
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

class ProfileForm(forms.ModelForm):
 
    firstname = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your firstname . . .",
            "id": "firstname",
            "type": "text",
        }),
        required=True,
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

    
    birth_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-control", "type": "date", "id": "birth_date"}),
        required=True
    )
    
    gender = forms.ChoiceField(
        choices=UserProfile.GENDER_CHOICES,
        widget=forms.Select(attrs={"class": "dropdown-item", "id": "gender"}),
        required=True
    )
    
    goal_weight = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            "class": "form-control", 
            "id": "goal_weight",
            "placeholder": "Please enter a numeric value . . .", 
            "step": "0.01"}),
        required=True,
        min_value=0
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name','password1', 'password2', 
                  'birth_date', 'gender', 'goal_weight',]

    def __init__(self, *args, **kwargs):
        user_instance = kwargs.pop('user_instance', None)
        profile_instance = kwargs.pop('profile_instance', None)
        super().__init__(*args, **kwargs)

        if user_instance and isinstance(user_instance, User):  # ตรวจสอบว่าเป็น instance ของ User
            self.initial['username'] = user_instance.username
            self.initial['email'] = user_instance.email
            self.initial['firstname'] = user_instance.first_name
            self.initial['lastname'] = user_instance.last_name
        
        if profile_instance and isinstance(profile_instance, UserProfile):  # ตรวจสอบว่าเป็น instance ของ UserProfile
            self.initial['goal_weight'] = profile_instance.goal_weight
            self.initial['gender'] = profile_instance.gender
            self.initial['birth_date'] = profile_instance.birth_date


            

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match")

        # เพิ่มการตรวจสอบชื่อผู้ใช้ที่มีอยู่แล้ว
        username = cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")

        # เพิ่มการตรวจสอบอีเมลที่มีอยู่แล้ว
        email = cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")

        print("Cleaned Data: ", cleaned_data)  # เพิ่มการพิมพ์ข้อมูลที่ถูก cleaned
        return 

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


