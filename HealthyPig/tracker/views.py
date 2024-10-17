from decimal import Decimal
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django import views
from django.db.models import F, Q, Sum
from django.contrib.auth import logout, login
from tracker.forms import FoodRecordForm, ExerciseRecordForm, MenuForm, ProfileForm, WeightForm
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

    def delete(self, request, food_id):
        """ลบอาหาร"""
        print("In the Delete already")
        getfood = Food.objects.get(id=food_id)
        getfood.delete()
        return redirect('staffpage')  # ส่งกลับไปยังหน้าที่ต้องการหลังจากลบ
    
class EditMenuView(views.View):
    def get(self, request, food_id):
        print(food_id)
        print("-----------------------------------------")
        """แสดงฟอร์มแก้ไขอาหาร"""
        getfood = get_object_or_404(Food, pk=food_id)  # Fetch the food object
        form = MenuForm(instance=getfood)  # Prepopulate the form with the food instance
        return render(request, 'editfood_form.html', {'form': form, 'food': getfood, 'food_id': food_id})
        # return redirect('editmenu')
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
        
# class AddCustomView(views.View):
#     def get(self, request):
#         form = CustomForm()
#         return render(request, "custom_form.html", {"form": form})
    
class ProfileView(views.View):
    def get(self, request):
        users = request.user
        user_profile = UserProfile.objects.get(user=request.user)
        form1 = ProfileForm(request.POST, users)
        # user_info = User_Info_Record.objects.get(user=users)
        # print(user_profile)
        # form1 = ProfileForm(user_instance=users, profile_instance=user_profile)
        # form1 = ProfileForm(user_instance=users, profile_instance=user_profile)
        context = {
            'form1': form1,
        }
        return render(request, "profile.html", context)

       
        
    # @transaction.atomic
    # def post(self, request):
    #     form = ProfileForm(request.POST, instance=request.user)
    #     user_profile = UserProfile.objects.get(user=request.user)
    #     if form.is_valid():
    #         user = form.save()
    #         user_profile, created = UserProfile.objects.get_or_create(user=user)
    #         print("UserProfile created:", created)  # Debug statement
    #         print("UserProfile before save:", user_profile.__dict__)  # Debug statement

    #         # อัปเดตข้อมูลใน UserProfile
    #         user_profile.birth_date = form.cleaned_data['birth_date']
    #         user_profile.gender = form.cleaned_data['gender']
    #         user_profile.goal_weight = float(form.cleaned_data['goal_weight'])
    #         user_profile.save()
    #         return redirect("mainpage")
    #     return render(request, "profile.html", {"form": form})
    def post(self, request):
        users = request.user
        
        # ตรวจสอบว่า UserProfile มีอยู่หรือไม่
        try:
            # user_profile = UserProfile.objects.get(user=users)
            user_instance = User.objects.get(pk=users.pk)  # ดึง User object ที่มี primary key = 1
            profile_instance = UserProfile.objects.get(user=user_instance)  # ดึง UserProfile object ที่สัมพันธ์กับ user_instance
        except UserProfile.DoesNotExist:
            # จัดการข้อผิดพลาดเมื่อไม่มี UserProfile
            form = ProfileForm()  # กำหนดค่าให้กับ form ไม่ให้เป็นตัวแปรท้องถิ่นที่ไม่ได้ถูกกำหนดค่า
            return render(request, "profile.html", {"form": form, "error": "User profile does not exist."})

        form1 = ProfileForm(request.POST, user_instance=user_instance, profile_instance=profile_instance)  # Ensure correct parameters
        
        print("Form Errors before validation:", form.errors)
        # เพิ่มการพิมพ์ค่า field ต่างๆ เพื่อตรวจสอบ
        print("Username: ", form['username'].value())
        print("Email: ", form['email'].value())
        print("Firstname: ", form['firstname'].value())
        print("Lastname: ", form['lastname'].value())
        print("Goal Weight: ", form['goal_weight'].value())

        print("Form Errors before validation:", form.errors)
        if form1.is_valid():
            print("Form is valid")
            user = form1.save(commit=False)  # ไม่บันทึกข้อมูล user ทันที
            user.save()  # บันทึก user หลังจากการตรวจสอบความถูกต้อง
            
            # อัปเดตข้อมูล UserProfile
            profile_instance.birth_date = form.cleaned_data['birth_date']
            profile_instance.gender = form.cleaned_data['gender']
            profile_instance.goal_weight = float(form.cleaned_data['goal_weight'])
            profile_instance.save()  # บันทึก UserProfile
            
            return redirect("mainpage")
        else:
            print(form.errors)
            return render(request, "profile.html", {"form1": form1, "error": "User profile does not exist."})

        

# class ProfileUpdateView(View):
#     @transaction.atomic
#     def post(self, request, pk):
#         # ตรวจสอบว่าผู้ใช้ที่เข้าสู่ระบบมี UserProfile หรือไม่
#         user =request.user
#         users = get_object_or_404(User, pk=pk)  # ใช้ pk เพื่อค้นหา UserProfile ตาม ID
#         user_profile = UserProfile.objects.get(user)  # ใช้ pk เพื่อค้นหา UserProfile ตาม ID

#         # สร้างฟอร์มจากข้อมูลที่ส่งมา
#         form = ProfileForm(request.POST, user_instance=request.user, profile_instance=user_profile)

#         print("Form Errors before validation:", form.errors)

#         if form.is_valid():
#             print("Form is valid")
            
#             # บันทึกข้อมูลผู้ใช้
#             user_instance = form.save(commit=False)  # ไม่บันทึกข้อมูลผู้ใช้ทันที
#             user_instance.save()  # บันทึก user หลังจากการตรวจสอบความถูกต้อง

#             # อัปเดตข้อมูล UserProfile
#             users.birth_date = form.cleaned_data['birth_date']
#             users.gender = form.cleaned_data['gender']
#             users.goal_weight = float(form.cleaned_data['goal_weight'])
#             users.save()  # บันทึก UserProfile
            
#             return JsonResponse({'message': 'Profile updated successfully'})  # ส่งคืนข้อความสำเร็จ

#         # ถ้าฟอร์มไม่ถูกต้อง ส่งคืนข้อผิดพลาด
#         return JsonResponse({'errors': form.errors}, status=400)

#     def get(self, request, pk):
#         user = get_object_or_404(User, pk=pk)
#         user_profile = get_object_or_404(UserProfile, user=user)
#         form = ProfileForm(user_instance=user, profile_instance=user_profile)
        
#         return render(request, "profile.html", {"form": form})

class WeightView(views.View):
    def get(self, request):
        # ตรวจสอบว่าผู้ใช้เข้าสู่ระบบหรือไม่
        # if request.user.is_authenticated:
            # try:
                # ดึงข้อมูลโปรไฟล์ของผู้ใช้
            user_profile = UserProfile.objects.get(user=request.user)

                # ดึงข้อมูล User_Info_Record ที่เชื่อมโยงกับ UserProfile
            user_info_record = User_Info_Record.objects.filter(user=user_profile).first()

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
        

#Chat GPT แนะนำมา 

# from django import forms
# from django.contrib.auth.models import User
# #ตรวจสอบ errerlist  <li>A user with that username already exists.</li>
# class UserRegistrationForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['username', 'password']
    
#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         if User.objects.filter(username=username).exists():
#             raise forms.ValidationError("A user with that username already exists.")
#         return username