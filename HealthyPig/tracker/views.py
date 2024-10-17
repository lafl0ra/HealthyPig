from decimal import Decimal
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django import views
from django.db.models import F, Q, Sum
from django.contrib.auth import logout, login
from tracker.forms import FoodRecordForm, ExerciseRecordForm, MenuForm, ProfileForm, WeightForm, ExerciseForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import UserProfile, Food, Exercise, FoodRecord, ExerciseRecord, User_Info_Record, User
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash


# exercise/food ห้ามลบ เพิ่มกับแก้ได้อย่างเดียว

# สำหรับการบันทึก datetime ใน Django นั้น โดยทั่วไปจะมีการตั้งค่า auto_now_add=True หรือ auto_now=True 
# ในฟิลด์ของ DateTimeField ในโมเดล ซึ่งจะช่วยให้ระบบบันทึกวันที่และเวลาลงไปโดยอัตโนมัติเมื่อมีการบันทึก (insert) 
# หรืออัพเดต (update) ข้อมูลในโมเดลโดยไม่ต้องเพิ่มค่ามาในฟอร์มหรือจาก view ครับ


class HomePageView(LoginRequiredMixin, views.View):
    login_url = '/authen/login/'
    def get(self, request):
        # form = AuthenticationForm()
        return render(request, 'homepage.html')
    




class MainPageView(LoginRequiredMixin, PermissionRequiredMixin, views.View):
    login_url = '/authen/login/'
    permission_required = [
        'tracker.view_food', 
        'tracker.view_exercise', 
        'tracker.view_foodrecord', 
        'tracker.view_exerciserecord'
    ]
    
    @transaction.atomic
    def get(self, request):
        today = timezone.localtime(timezone.now()).date()
        foods = Food.objects.all().order_by('id')
        exercises = Exercise.objects.all().annotate(
            calories_burned_per_hour=F('calories_burned_per_min') * 60
        ).order_by('id')
        
        if request.user.is_staff:
            user_profile = None
            today_food = today_ex = sumkcal = percentkcal = None
        else:
            user_profile = UserProfile.objects.get(user=request.user)
            today_food = FoodRecord.objects.filter(
                user=request.user, 
                datetime_record__date=today
            ).aggregate(total=Sum('sum_calories'))['total'] or Decimal('0.00')
            
            today_ex = ExerciseRecord.objects.filter(
                user=request.user, 
                datetime_record__date=today
            ).aggregate(total=Sum('sum_calories'))['total'] or Decimal('0.00')
            
            sumkcal = today_food - today_ex
            percentkcal = (sumkcal / user_profile.TDEE) * 100

        query = request.GET  # For search field handling
        
        # Normalize calories and quantities to integers if they have no decimal value
        for food in foods:
            if food.calories is None:
                food.calories = 0
            elif food.calories == int(food.calories):
                food.calories = int(food.calories)
                
            if food.quantity_in_grams is None:
                food.quantity_in_grams = 0
            elif food.quantity_in_grams == int(food.quantity_in_grams):
                food.quantity_in_grams = int(food.quantity_in_grams)
                
        for exercise in exercises:
            if exercise.calories_burned_per_min == int(exercise.calories_burned_per_min):
                exercise.calories_burned_per_min = int(exercise.calories_burned_per_min)
            if exercise.calories_burned_per_hour == int(exercise.calories_burned_per_hour):
                exercise.calories_burned_per_hour = int(exercise.calories_burned_per_hour)
        
        # Search functionality
        if query.get("search"):
            search_term = query.get("search")
            foods = foods.filter(
                Q(name__icontains=search_term) | 
                Q(user__username__icontains=search_term)
            )
            
        if query.get("search2"):
            search_term = query.get("search2")
            exercises = exercises.filter(
                Q(name__icontains=search_term)
            )
                
        return render(request, 'mainpage.html', {
            'user_profile': user_profile,
            'foods': foods,
            'exercises': exercises,
            'today_food': today_food,
            'today_ex': today_ex,
            'sumkcal': sumkcal,
            'percentkcal': percentkcal
        })
    










class FoodDetailListView(LoginRequiredMixin, PermissionRequiredMixin, views.View):
    login_url = '/authen/login/'
    permission_required = [
        'tracker.view_food'
    ]
    def get(self, request, pk):
        food = get_object_or_404(Food, pk=pk)  # Fetch the food object
        form = FoodRecordForm(instance=food)  # Prepopulate the form with the food instance
        return render(request, 'fooddetail.html', {'form': form, 'food': food, 'pk':pk})

    @transaction.atomic
    def post(self, request, pk):  # รับ pk สำหรับ food
        form = FoodRecordForm(request.POST)
        
        if form.is_valid():
            amount = form.cleaned_data['amount']  # เข้าถึงข้อมูลที่ผ่านการตรวจสอบแล้ว
            food = get_object_or_404(Food, pk=pk)  # ดึง Food object ตาม pk
            user = request.user  # ดึง user จาก request
            
            # คำนวณแคลอรี่รวมจากปริมาณอาหาร
            sum_calories = amount * food.calories  # คำนวณแคลอรี่ที่ได้รับ
            
            # สร้าง FoodRecord ใหม่
            food_record = FoodRecord(
                food=food,
                user=user,
                amount=amount,
                sum_calories=sum_calories
            )
            food_record.save()  # บันทึกข้อมูล

            # ส่งกลับไปที่หน้า mainpage โดยส่ง ID ไปด้วย
            return redirect('mainpage')  # ส่ง ID ของผู้ใช้กลับไปด้วย

        # ถ้าฟอร์มไม่ถูกต้อง ส่งกลับไปยังหน้า food detail
        food = get_object_or_404(Food, pk=pk)  # ดึง Food object ตาม pk
        return render(request, 'fooddetail.html', {'form': form, 'food': food})
    












class ExerciseDetailListView(LoginRequiredMixin, PermissionRequiredMixin, views.View):
    login_url = '/authen/login/'
    permission_required = [
        'tracker.view_exerciserecord',
        'tracker.add_exerciserecord',
    ]
    def get(self, request, pk):
        exercise = get_object_or_404(Exercise, pk=pk)  # Fetch the exercise object
        form = ExerciseRecordForm(instance=exercise)  # Prepopulate the form with the exercise instance
        return render(request, 'exercisedetail.html', {'form': form, 'exercise': exercise})

    @transaction.atomic
    def post(self, request, pk):  # รับ pk สำหรับ exercise
        form = ExerciseRecordForm(request.POST)
        
        if form.is_valid():
            amount = form.cleaned_data['amount']  # เข้าถึงข้อมูลที่ผ่านการตรวจสอบแล้ว
            exercise = get_object_or_404(Exercise, pk=pk)  # ดึง Exercise object ตาม pk
            user = request.user  # ดึง user จาก request
            
            # คำนวณแคลอรี่รวมจากการออกกำลังกาย
            sum_calories = amount * exercise.calories_burned_per_min  # คำนวณแคลอรี่ที่เผาผลาาญ
            
            # สร้าง ExerciseRecord ใหม่
            ex_record = ExerciseRecord(
                exercise=exercise,
                user=user,
                amount=amount,
                sum_calories=sum_calories
            )
            ex_record.save()  # บันทึกข้อมูล

            # ส่งกลับไปที่หน้า mainpage โดยส่ง ID ไปด้วย
            return redirect('mainpage')  # ส่ง ID ของผู้ใช้กลับไปด้วย

        # ถ้าฟอร์มไม่ถูกต้อง ส่งกลับไปยังหน้า exercise detail
        exercise = get_object_or_404(Exercise, pk=pk)  # ดึง Exercise object ตาม pk
        return render(request, 'exercisedetail.html', {'form': form, 'exercise': exercise})














class ProgressOverviewView(LoginRequiredMixin, PermissionRequiredMixin, views.View):
    login_url = '/authen/login/'
    permission_required = [
        'tracker.view_foodrecord',
        'tracker.view_exerciserecord',
    ]
    def get(self, request, pk):
        # Get the current user
        userr = request.user
        if userr.is_staff:
            userr = get_object_or_404(User, pk=pk)
            print(userr.username)
        
        userpro = UserProfile.objects.get(user=userr)
        
        food_records = FoodRecord.objects.filter(user=userr)  # แก้ไขให้ตรงกับโมเดลของคุณ
        ex_records = ExerciseRecord.objects.filter(user=userr)  # แก้ไขให้ตรงกับโมเดลของคุณ
        
        # Food records: Sum calories grouped by date
        food_data = (
            FoodRecord.objects.filter(user=userr)
            .values('datetime_record__date')  # Group by date
            .annotate(total_food_calories=Sum('sum_calories'))  # Sum calories for food
            .order_by('datetime_record__date')
        )

        # Exercise records: Sum calories grouped by date
        exercise_data = (
            ExerciseRecord.objects.filter(user=userr)
            .values('datetime_record__date')  # Group by date
            .annotate(total_exercise_calories=Sum('sum_calories'))  # Sum calories for exercise
            .order_by('datetime_record__date')
        )
        
        weight_data = (
            User_Info_Record.objects.filter(user=userpro)
            .order_by('-datetime_update')  # เรียงข้อมูลตามวันเวลาอัปเดตล่าสุด
        )

        latest_weight = weight_data.first()  # ดึงข้อมูลน้ำหนักล่าสุด

        # Merging food and exercise data by date
        calorie_summary = []
        food_dict = {item['datetime_record__date']: item['total_food_calories'] for item in food_data}
        exercise_dict = {item['datetime_record__date']: item['total_exercise_calories'] for item in exercise_data}

        # Combine both records based on the date
        all_dates = set(food_dict.keys()).union(set(exercise_dict.keys()))
        for date in all_dates:
            food_calories = food_dict.get(date, 0)
            exercise_calories = exercise_dict.get(date, 0)
            net_calories = food_calories - exercise_calories  # Calculate net calories
            calorie_summary.append({
                'date': date,
                'total_calories': net_calories,
            })
        

        if userr.is_authenticated:  # เช็คว่า user มีการล็อกอินอยู่
            # ดึงข้อมูลอาหารทั้งหมดของผู้ใช้แล้วทำการรวม sum_calories ตามวันที่
            daily_data = (
                FoodRecord.objects
                .filter(user=userr)  # กรองข้อมูลตามผู้ใช้ที่ล็อกอิน
                .annotate(date=TruncDate('datetime_record'))  # แปลงเป็นวันที่
                .values('date')
                .annotate(total_calories=Sum('sum_calories'))  # รวมค่า sum_calories
                .order_by('date')  # จัดเรียงตามวันที่
            )

            # สร้าง list สำหรับ JavaScript
            labels = [entry['date'].strftime('%Y-%m-%d') for entry in daily_data]
            calories = [entry['total_calories'] or 0 for entry in daily_data]  # กำหนดค่าเริ่มต้นเป็น 0
        else:
            # ถ้าไม่มีผู้ใช้ล็อกอิน ให้ส่งค่าเริ่มต้น
            labels = []
            calories = []
            
        context = {
            'food_records': food_records,
            'ex_records': ex_records,
            'daily_data': daily_data,
            'labels': labels,
            'calories': calories,
            'calorie_summary': calorie_summary,
            'weight_data' : weight_data,
            'latest_weight': latest_weight,
        }
        return render(request, 'progress.html', context)












class StaffPageView(LoginRequiredMixin, views.View):
    login_url = '/login/'
    def get(self, request):
        query = request.GET
        foods = Food.objects.all().order_by('id') # จัดเรียงตาม id
        exercises = Exercise.objects.all().order_by('id') # จัดเรียงตาม id
        users = User.objects.filter(is_staff = False).order_by('id')  # จัดเรียงตาม id
        

        # เช็คว่ามีคำค้นหาหรือไม่
        food_search = foods
        exercise_search =  exercises
        user_search = users
        if query.get("search_food"):
            food_search = foods.filter(
                Q(name__icontains=query.get("search_food"))
                )
        if query.get("search_exercise"):
            exercise_search = exercises.filter(
                Q(name__icontains=query.get("search_exercise"))
                )
        if query.get("search_user"):
            user_search = users.filter(
                Q(username__icontains=query.get("search_user"))|
                Q(id__icontains=query.get("search_user"))|
                Q(first_name__icontains=query.get("search_user"))|
                Q(last_name__icontains=query.get("search_user"))
                )
        
        context = {'foods': food_search, 'exercises' : exercise_search, 'users': user_search}
        return render(request, 'staffpage.html', context)
    














class UserRecordView(LoginRequiredMixin, views.View):
    login_url = '/login/'
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    # def get(self, request, pk, format=None):
    #     appointments = self.get_object(pk)
        # serializer = AppointmentSerializer(appointments)
        # return Response(serializer.data)

    @transaction.atomic
    def get(self, request, pk, format=None):
        query = request.GET
        users = self.get_object(pk)
        food_record = FoodRecord.objects.filter(user=users)
        exercise_record = ExerciseRecord.objects.filter(user=users)
    
        # เช็คว่ามีคำค้นหาหรือไม่
        food_search = food_record
        exercise_search =  exercise_record

        if query.get("search_food"):
            food_search = food_record.filter(
                Q(foodrecord__name__icontains=query.get("search_food"))|
                Q(amount__icontains=query.get("search_food"))|
                Q(sum_calories__icontains=query.get("search_food"))
                )
        if query.get("search_exercise"):
            exercise_search = exercise_record.filter(
                Q(exercise__name__icontains=query.get("search_exercise"))|
                Q(amount__icontains=query.get("search_exercise"))| # ติดปัญหาตรงที่ไม่สามารถ search เลข int ได้
                Q(sum_calories__icontains=query.get("search_exercise"))
                )

        context = {'foods': food_search, 'exercises' : exercise_search, 'users': users}
        return render(request, 'user_record.html', context)
















class StaffPageView(views.View):
    def get(self, request):
        query = request.GET
        foods = Food.objects.all().order_by('id') # จัดเรียงตาม id
        exercises = Exercise.objects.all().order_by('id') # จัดเรียงตาม id
        users = User.objects.filter(is_staff = False).order_by('id')  # จัดเรียงตาม id
        

        # เช็คว่ามีคำค้นหาหรือไม่
        food_search = foods
        exercise_search =  exercises
        user_search = users
        if query.get("search_food"):
            food_search = foods.filter(
                Q(name__icontains=query.get("search_food"))
                )
        if query.get("search_exercise"):
            exercise_search = exercises.filter(
                Q(name__icontains=query.get("search_exercise"))
                )
        if query.get("search_user"):
            user_search = users.filter(
                Q(username__icontains=query.get("search_user"))|
                Q(id__icontains=query.get("search_user"))|
                Q(first_name__icontains=query.get("search_user"))|
                Q(last_name__icontains=query.get("search_user"))
                )
        
        context = {'foods': food_search, 'exercises' : exercise_search, 'users': user_search}
        return render(request, 'staffpage.html', context)
    















class AddMenuView(LoginRequiredMixin, views.View):
    login_url = '/login/'
    
    def get(self, request):
        """แสดงฟอร์มเพิ่มหรือแก้ไขอาหาร"""
        form = MenuForm()
        users = User.objects.all()
        context = {'users': users, "form": form}
        return render(request, 'menu_form.html', context)

    @transaction.atomic
    def post(self, request):
        """จัดการการเพิ่มอาหาร"""
        food_id = request.POST.get('food_id')  # Retrieve the food_id from POST data
        action = request.POST.get('submit')
        user = request.user
        getuser = User.objects.get(id=user.id)

        # ตรวจสอบว่ามีคำขอลบหรือไม่
        if action == 'delete':
            self.delete(request, food_id)
            return redirect('staffpage')
        
        else:  # ถ้าไม่มี สร้างอาหารใหม่
            print("yaaaaaaaaaaaaaaaaa")
            form = MenuForm(request.POST)
            if form.is_valid():
                food_form = form.save(commit=False)
                food_form.user_id = getuser.id
                food_form.save()
                form.save_m2m()  # บันทึก many-to-many relationship
                return redirect('staffpage')  # ส่งไปยังหน้าถัดไปเมื่อบันทึกเสร็จ
            else:
                # ถ้าฟอร์มไม่ถูกต้อง ให้แสดงฟอร์มพร้อมกับข้อผิดพลาด
                print("not valid")
                print(form.errors)  # เพิ่มการตรวจสอบข้อผิดพลาด
                users = User.objects.all()
                return render(request, "menu_form.html", {"form": form, "users": users, 'food_id': food_id})

    @transaction.atomic
    def delete(self, request, food_id):
        """ลบอาหาร"""
        print("In the Delete already")
        getfood = Food.objects.get(id=food_id)
        getfood.delete()
        return redirect('staffpage')  # ส่งกลับไปยังหน้าที่ต้องการหลังจากลบ
    













class EditMenuView(LoginRequiredMixin, views.View):
    login_url = '/login/'
    def get(self, request, food_id):
        """แสดงฟอร์มแก้ไขอาหาร"""
        getfood = get_object_or_404(Food, pk=food_id)  # Fetch the food object
        form = MenuForm(instance=getfood)  # Prepopulate the form with the food instance
        return render(request, 'editfood_form.html', {'form': form, 'food': getfood, 'food_id': food_id})
        # return redirect('editmenu')

    @transaction.atomic
    def post(self, request, food_id):
        """จัดการฟอร์มแก้ไขอาหาร"""
        getfood = get_object_or_404(Food, pk=food_id)
        form = MenuForm(request.POST, instance=getfood)
            
        if form.is_valid():  # ตรวจสอบว่าแบบฟอร์มถูกต้องหรือไม่
            print("Can valid")
            print("ba ba bo bo")
            form.save()  # บันทึกการเปลี่ยนแปลงใน getfood
            return redirect('fooddetail')
        else:
            # ถ้าฟอร์มไม่ถูกต้อง ให้แสดงฟอร์มพร้อมกับข้อผิดพลาด
            print("not valid")
            # print(form.clean_name)
            users = User.objects.all()
            return render(request, "editfood_form.html", {"form": form, "users": users, 'food_id': food_id})












class AddExerciseView(LoginRequiredMixin, views.View):
    login_url = '/login/'
    
    def get(self, request):
        """แสดงฟอร์มเพิ่มหรือแก้ไขการออกกำลังกาย"""
        form = ExerciseForm()
        users = User.objects.all()
        context = {'users': users, "form": form}
        return render(request, 'exercise_form.html', context)

    @transaction.atomic
    def post(self, request):
        """จัดการการเพิ่มการออกกำลังกาย"""
        exercise_id = request.POST.get('exercise_id')  
        user = request.user
        getuser = User.objects.get(id=user.id)
        form = MenuForm(request.POST)
        if form.is_valid():
            exercise_form = form.save(commit=False)
            exercise_form.user_id = getuser.id
            exercise_form.save()
            # form.save_m2m()  # บันทึก many-to-many relationship
            return redirect('staffpage')  # ส่งไปยังหน้าถัดไปเมื่อบันทึกเสร็จ
        else:
            # ถ้าฟอร์มไม่ถูกต้อง ให้แสดงฟอร์มพร้อมกับข้อผิดพลาด
            print("not valid")
            print(form.errors)  # เพิ่มการตรวจสอบข้อผิดพลาด
            users = User.objects.all()
            return render(request, "menu_form.html", {"form": form, "users": users, 'exercise_id': exercise_id})








class EditExerciseView(LoginRequiredMixin, views.View):
    login_url = '/login/'
    def get(self, request, ex_id):
        """แสดงฟอร์มแก้ไขออกกำลังกาย"""
        getexercise = get_object_or_404(Exercise, pk=ex_id)  # Fetch the food object
        form = ExerciseForm(instance=getexercise)  # Prepopulate the form with the food instance
        return render(request, 'editexercise_form.html', {'form': form, 'food': getexercise, 'ex_id': ex_id})
    

    @transaction.atomic
    def post(self, request, ex_id):
        """จัดการฟอร์มแก้ไขออกกำลังกาย"""
        getexercise = get_object_or_404(Exercise, pk=ex_id)
        form = ExerciseForm(request.POST, instance=getexercise)
            
        if form.is_valid():  # ตรวจสอบว่าแบบฟอร์มถูกต้องหรือไม่
            print("Can valid")
            print("ba ba bo bo")
            form.save()  # บันทึกการเปลี่ยนแปลงใน getfood
            return redirect('exercisedetail')
        else:
            # ถ้าฟอร์มไม่ถูกต้อง ให้แสดงฟอร์มพร้อมกับข้อผิดพลาด
            print("not valid")
            # print(form.clean_name)
            users = User.objects.all()
            return render(request, "editexercise_form.html", {"form": form, "users": users, 'ex_id': ex_id})






from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from .forms import CustomPasswordChangeForm, ProfileForm  # นำเข้า ProfileForm
from tracker.models import UserProfile

@method_decorator(login_required, name='dispatch')
class ProfileView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/authen/login/'
    permission_required = [
        'tracker.view_userprofile',
        'tracker.change_userprofile',
        'auth.change_user',
        'auth.view_user'
    ]

    def get(self, request):
        user_profile = get_object_or_404(UserProfile, user=request.user)
        form1 = ProfileForm(user_instance=request.user, profile_instance=user_profile)
        context = {'form1': form1}
        return render(request, "profile.html", context)

    def post(self, request):
        user = request.user
        user_profile = get_object_or_404(UserProfile, user=user)

        form1 = ProfileForm(request.POST, user_instance=user, profile_instance=user_profile)

        if form1.is_valid():
            user = form1.save(commit=False)  # เก็บข้อมูลไว้ก่อนยังไม่บันทึกลงฐานข้อมูล
            password1 = form1.cleaned_data.get('password1')

            if password1:
                user.set_password(password1)
                update_session_auth_hash(request, user)  # ให้ผู้ใช้ล็อกอินต่อหลังเปลี่ยนรหัสผ่าน

            user.save()  # บันทึกข้อมูลผู้ใช้ลงฐานข้อมูล
            user_profile.save()  # บันทึกข้อมูลโปรไฟล์

            messages.success(request, "Your profile was updated successfully.")
            return redirect("mainpage")
        else:
            messages.error(request, "Please correct the error(s) below.")
            return render(request, "profile.html", {"form1": form1})
        
# @method_decorator(login_required, name='dispatch')
# class ProfileView(LoginRequiredMixin, PermissionRequiredMixin, views.View):
#     login_url = '/authen/login/'
#     permission_required = [
#         'tracker.view_userprofile',
#         'tracker.change_userprofile',
#         'auth.change_user',
#         'auth.view_user'
#     ]
#     def get(self, request):
#         # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
#         user_profile = get_object_or_404(UserProfile, user=request.user)
#         form1 = ProfileForm(user_instance=request.user, profile_instance=user_profile)
#         context = {
#             'form1': form1,
#         }
#         return render(request, "profile.html", context)

#     def post(self, request):
#         # print('--------------------------------------------------------------------------------')
#         user = request.user
#         user_profile = get_object_or_404(UserProfile, user=user)
#         # ใส่ข้อมูลลงฟอร์ม
#         form1 = ProfileForm(request.POST, user_instance=user, profile_instance=user_profile)

#         if form1.is_valid():
#             user = form1.save(commit=False)  # บันทึกข้อมูลผู้ใช้โดยไม่ทำการบันทึกลงฐานข้อมูลทันที
#             password1 = form1.cleaned_data.get('password1')
            
#             if password1:
#                 user.set_password(password1)
#                 update_session_auth_hash(request, user)  # ทำให้ผู้ใช้ยังคงล็อกอินอยู่หลังจากเปลี่ยนรหัสผ่าน

#             user.save()  # บันทึกข้อมูลผู้ใช้ที่อัปเดตแล้ว

#             # อัปเดตข้อมูล UserProfile
#             user_profile.birth_date = form1.cleaned_data.get('birth_date', user_profile.birth_date)
#             user_profile.gender = form1.cleaned_data.get('gender', user_profile.gender)
#             user_profile.goal_weight = form1.cleaned_data.get('goal_weight', user_profile.goal_weight)
#             user_profile.save()  # บันทึกข้อมูลโปรไฟล์ที่อัปเดตแล้ว

#             return redirect("mainpage")
#         else:
#             # แสดงฟอร์มพร้อมกับข้อผิดพลาดหากฟอร์มไม่ถูกต้อง
#             return render(request, "profile.html", {"form1": form1})












class WeightView(LoginRequiredMixin, PermissionRequiredMixin, views.View):
    login_url = '/authen/login/'
    permission_required = [
        'tracker.change_user_info_record',
        'tracker.view_user_info_record',
    ]
    def get(self, request):
        # if request.user.is_authenticated:
            # try:
                # ดึงข้อมูลโปรไฟล์ของผู้ใช้
            user_profile = UserProfile.objects.get(user=request.user)

                # ดึงข้อมูล User_Info_Record ที่เชื่อมโยงกับ UserProfile
            user_info_record = User_Info_Record.objects.filter(user=user_profile).last()

                # ตรวจสอบว่ามีข้อมูล User_Info_Record หรือไม่
            if user_info_record:
                    # ถ้ามี ให้ดึงค่า weight มา
                initial_weight = user_info_record.weight
            else:
                initial_weight = None  # หรือค่าที่เหมาะสมถ้าไม่มี

            # except UserProfile.DoesNotExist:
            #     return render(request, "error.html", {"message": "User profile not found."})

            # สร้างฟอร์มด้วย weight จาก User_Info_Record
            form2 = WeightForm(initial={'weight': initial_weight}) 
            # form2 = WeightForm(instance=user_profile)
            context = {
                'form2': form2,
            }
            return render(request, "changeweight.html", context)
        # else:
        #     return redirect('login')  # เปลี่ยนเป็น URL ที่เหมาะสม
        
    @transaction.atomic
    def post(self, request):
        # ดึงข้อมูลโปรไฟล์ของผู้ใช้
        user_profile = UserProfile.objects.get(user=request.user).id
        # ดึงข้อมูล User_Info_Record ที่เชื่อมโยงกับ UserProfile
        # user_info_record = User_Info_Record.objects.filter(user=user_profile).last()
        form = WeightForm(request.POST)
        if form.is_valid():
                    # ถ้ามี ให้ดึงค่า weight มา
            # user_info_record.weight = form.cleaned_data['weight']
            # user_info_record.save()
            record_count = User_Info_Record.objects.count()
            new_record_id = record_count + 1
            datetime_update = datetime.today()
            user_info_record = User_Info_Record(
                id=new_record_id,
                datetime_update=datetime_update,
                user_id=user_profile,  # ตั้งค่า user ให้กับโปรไฟล์ของผู้ใช้
                weight=form.cleaned_data['weight']  # รับค่า weight จากฟอร์ม
            )
            user_info_record.save()  # บันทึก User_Info_Record ใหม่
            
            return redirect("profile")
        return render(request, "changeweight.html", {"form": form})










# views.py
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from .forms import CustomPasswordChangeForm

class ChangePasswordView(LoginRequiredMixin, View):
    def get(self, request):
        form = CustomPasswordChangeForm(user=request.user)  # กำหนด user ที่นี่
        return render(request, 'changepass.html', {'form': form})

    def post(self, request):
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)  # กำหนด user ที่นี่
        if form.is_valid():
            user = form.save()  # บันทึกรหัสผ่านใหม่
            update_session_auth_hash(request, user)  # ให้ผู้ใช้ยังล็อกอินอยู่หลังจากเปลี่ยนรหัสผ่าน
            return redirect('mainpage')  # เปลี่ยนไปยังหน้าหลักหรือตามที่ต้องการ
        return render(request, 'changepass.html', {'form': form})
