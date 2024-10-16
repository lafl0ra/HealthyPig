from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from authen.forms import RegisterForm
from django.db import IntegrityError, transaction
from datetime import datetime
from tracker.models import UserProfile, User_Info_Record


class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {"form": form})
    
    @transaction.atomic  # ใช้วิธี atomic decorator
    def post(self, request):
        form = AuthenticationForm(data=request.POST)  # Instantiate form with POST data
        if form.is_valid():
            user = form.get_user()  # Get the user object from the form
            login(request, user)  # Log in the user
            
            # Redirect based on whether the user is a staff member
            if user.is_staff:
                return redirect('staffpage')  # Redirect staff to the staff page
            else:
                return redirect('mainpage')  # Redirect regular users to the main page

        # If the form is not valid, render the login page again with the form and errors
        return render(request, 'login.html', {"form": form})

class LogoutView(View): 
    
    def get(self, request):
        logout(request)
        return redirect('login')

class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'register.html', {"form": form})
    
    @transaction.atomic  # ใช้วิธี atomic decorator
    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            birth_date = form.cleaned_data['birth_date']
            gender = form.cleaned_data['gender']
            height = float(form.cleaned_data['height'])
            weight = float(form.cleaned_data['weight'])
            goal_weight = float(form.cleaned_data['goal_weight'])

            # Calculate values
            today = datetime.today() 
            age = today.year - birth_date.year  
            if (today.month, today.day) < (birth_date.month, birth_date.day): 
                age -= 1
            
            BMI = weight / (height / 100) ** 2
            BMR = 0
            if gender == "F":
                BMR = 665 + (9.6 * weight) + (1.8 * height) - (4.7 * age)
            else: 
                BMR = 66 + (13.7 * weight) + (5 * height) - (6.8 * age)

            TDEE = 0
            activity_level = form.cleaned_data['activity']
            if activity_level == 'sedentary':
                TDEE = BMR * 1.2
            elif activity_level == 'light':
                TDEE = BMR * 1.375
            elif activity_level == 'moderate':
                TDEE = BMR * 1.55
            elif activity_level == 'active':
                TDEE = BMR * 1.725
            elif activity_level == 'very_active':
                TDEE = BMR * 1.9
            
            goal_weight_per_week = form.cleaned_data['goal_weight_per_week']
            goal_amount_day = 0
            if goal_weight_per_week == 'easy':
                goal_amount_day = (goal_weight / 0.25) * 7
            elif goal_weight_per_week == 'recommend':
                goal_amount_day = (goal_weight / 0.33) * 7
            elif goal_weight_per_week == 'normal':
                goal_amount_day = (goal_weight / 0.5) * 7
            elif goal_weight_per_week == 'hard':
                goal_amount_day = (goal_weight / 1) * 7

            # Use transaction.atomic() to ensure both tables are saved together
                    # Update the user if needed
                    # user.some_field = some_value  # Example if you need to update User fields

                    # Create UserProfile instance
            new_userprofile = UserProfile(
                        user=user,
                        birth_date=birth_date,
                        gender=gender,
                        height=height,
                        BMI=BMI,
                        BMR=BMR,
                        TDEE=TDEE,
                        goal_amount_day=goal_amount_day,
                        goal_weight=goal_weight
                    )

                    # Create User_Info_Record instance
            datetime_update = datetime.today()
            # Get the count of records
            record_count = User_Info_Record.objects.count()

            # Create the new record with an ID based on the count
            new_record_id = record_count + 1

            user_info_record = User_Info_Record(
                id=new_record_id,
                datetime_update=datetime_update,
                weight=weight,
                user=new_userprofile,  # link to the user instance directly
            )

            user.save()
            new_userprofile.save()
            user_info_record.save()
            # group = Group.objects.get(name='Customer')
            # user.groups.add(group)

            return redirect('login')
        else:
            print(form.errors)
            return render(request, "register.html", {"form": form})
