from decimal import Decimal
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django import views
from django.db.models import F, Q, Sum
from django.contrib.auth import logout, login
from tracker.forms import FoodRecordForm, ExerciseRecordForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import UserProfile, Food, Exercise, FoodRecord, ExerciseRecord, User_Info_Record
from django.utils import timezone
from django.db.models.functions import TruncDate

# exercise/food ห้ามลบ เพิ่มกับแก้ได้อย่างเดียว

# สำหรับการบันทึก datetime ใน Django นั้น โดยทั่วไปจะมีการตั้งค่า auto_now_add=True หรือ auto_now=True 
# ในฟิลด์ของ DateTimeField ในโมเดล ซึ่งจะช่วยให้ระบบบันทึกวันที่และเวลาลงไปโดยอัตโนมัติเมื่อมีการบันทึก (insert) 
# หรืออัพเดต (update) ข้อมูลในโมเดลโดยไม่ต้องเพิ่มค่ามาในฟอร์มหรือจาก view ครับ

class HomePageView(views.View):
    def get(self, request):
        # form = AuthenticationForm()
        return render(request, 'homepage.html')
    
class MainPageView(views.View):
    def get(self, request):
        # form = AuthenticationForm()
        # today = timezone.now().date()
        today = timezone.localtime(timezone.now()).date()
        user_profile = UserProfile.objects.get(user=request.user)
        foods = Food.objects.all().order_by('id')
        exercises = Exercise.objects.all().annotate(
            calories_burned_per_hour=F('calories_burned_per_min') * 60
            ).order_by('id')
        today_food = FoodRecord.objects.filter(user=request.user,datetime_record__date=today).aggregate(total=Sum('sum_calories'))['total'] or Decimal('0.00')
        today_ex = ExerciseRecord.objects.filter(user=request.user,datetime_record__date=today).aggregate(total=Sum('sum_calories'))['total'] or Decimal('0.00')
        query = request.GET  # ใช้สำหรับฟิลด์ค้นหา
        
        sumkcal = today_food - today_ex
        percentkcal = (sumkcal / (user_profile.TDEE)) * 100
        
        # เช็คว่าเป็น none ไหม
        # เช็คว่าเป็นทศนิยมไหม แต่ถ้าไม่มีค่าทศนิยมให้แสดงค่าเป็น int เลย (ตัดจุดออก)
        for food in foods:
            if food.calories is None:
                food.calories = 0  # Set a default value for None
            elif food.calories == int(food.calories):
                food.calories = int(food.calories)    
                
        # เช็คว่าเป็น none ไหม
        # เช็คว่าเป็นทศนิยมไหม แต่ถ้าไม่มีค่าทศนิยมให้แสดงค่าเป็น int เลย (ตัดจุดออก)
        for food in foods:
            if food.quantity_in_grams is None:
                food.quantity_in_grams = 0  # Set a default value for None
            elif food.quantity_in_grams == int(food.quantity_in_grams):
                food.quantity_in_grams = int(food.quantity_in_grams)
        
        # เช็คว่าเป็นทศนิยมไหม แต่ถ้าไม่มีค่าทศนิยมให้แสดงค่าเป็น int เลย (ตัดจุดออก)
        for exercise in exercises:
            if exercise.calories_burned_per_min == int(exercise.calories_burned_per_min):
                exercise.calories_burned_per_min = int(exercise.calories_burned_per_min)
        
        # เช็คว่าเป็นทศนิยมไหม แต่ถ้าไม่มีค่าทศนิยมให้แสดงค่าเป็น int เลย (ตัดจุดออก)
        for exercise in exercises:
            if exercise.calories_burned_per_hour == int(exercise.calories_burned_per_hour):
                exercise.calories_burned_per_hour = int(exercise.calories_burned_per_hour)
                
        # เช็คว่ามีคำค้นหาหรือไม่
        if query.get("search"):
            search_term = query.get("search")
            # ค้นหาโดยใช้ชื่ออาหารหรือคำบรรยาย
            foods = foods.filter(
                Q(name__icontains=search_term) | 
                Q(description__icontains=search_term) |
                Q(user__username__icontains=search_term)  # ถ้าต้องการค้นหาตามชื่อผู้ใช้ด้วย
            )
        # เช็คว่ามีคำค้นหาหรือไม่
        if query.get("search2"):
            search_term = query.get("search2")
            exercises = exercises.filter(
                Q(name__icontains=search_term) | 
                Q(description__icontains=search_term)
            )
                
        return render(request, 'mainpage.html', {
            'user_profile': user_profile,
            'foods' : foods,
            'exercises' : exercises,
            'today_food': today_food,
            'today_ex': today_ex,
            'sumkcal': sumkcal,
            'percentkcal': percentkcal
        })

class FoodDetailListView(views.View):
    def get(self, request, pk):
        food = get_object_or_404(Food, pk=pk)  # Fetch the food object
        form = FoodRecordForm(instance=food)  # Prepopulate the form with the food instance
        return render(request, 'fooddetail.html', {'form': form, 'food': food})

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
    
class ExerciseDetailListView(views.View):
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
        return render(request, 'Exercisedetail.html', {'form': form, 'exercise': exercise})

class ProgressOverviewView(views.View):
    def get(self, request):
        user = request.user  # Get the logged-in user
        food_records = FoodRecord.objects.filter(user=request.user)  # แก้ไขให้ตรงกับโมเดลของคุณ
        ex_records = ExerciseRecord.objects.filter(user=request.user)  # แก้ไขให้ตรงกับโมเดลของคุณ
        
        # Food records: Sum calories grouped by date
        food_data = (
            FoodRecord.objects.filter(user=user)
            .values('datetime_record__date')  # Group by date
            .annotate(total_food_calories=Sum('sum_calories'))  # Sum calories for food
            .order_by('datetime_record__date')
        )

        # Exercise records: Sum calories grouped by date
        exercise_data = (
            ExerciseRecord.objects.filter(user=user)
            .values('datetime_record__date')  # Group by date
            .annotate(total_exercise_calories=Sum('sum_calories'))  # Sum calories for exercise
            .order_by('datetime_record__date')
        )
        
        userpro = UserProfile.objects.get(user=user)
        
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
        

        if user.is_authenticated:  # เช็คว่า user มีการล็อกอินอยู่
            # ดึงข้อมูลอาหารทั้งหมดของผู้ใช้แล้วทำการรวม sum_calories ตามวันที่
            daily_data = (
                FoodRecord.objects
                .filter(user=user)  # กรองข้อมูลตามผู้ใช้ที่ล็อกอิน
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
