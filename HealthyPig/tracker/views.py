from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
# from blogs.forms import BlogForm
from django.core.exceptions import PermissionDenied
from django import views
# from blogs.models import Blog
from django.db.models import F
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from .models import UserProfile, Food, Exercise


# exercise/food ห้ามลบ เพิ่มกับแก้ได้อย่างเดียว

class HomePageView(views.View):
    # login_url = "/authen/"
    # permission_required = [".view_blog"]
    def get(self, request):
        # form = AuthenticationForm()
        return render(request, 'homepage.html')
    
class MainPageView(views.View):
    # login_url = "/authen/"
    # permission_required = [".view_blog"]
    def get(self, request):
        # form = AuthenticationForm()
        user_profile = UserProfile.objects.get(user=request.user)
        foods = Food.objects.all().order_by('id')
        exercises = Exercise.objects.all().annotate(
            calories_burned_per_hour=F('calories_burned_per_min') * 60
            ).order_by('id')
        query = request.GET  # ใช้สำหรับฟิลด์ค้นหา
        
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
        })
    
     
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

# class BlogDetailView(views.View):
#     # login_url = "/authen/"
# # permission_required = ["blogs.view_blog"] 
    
#     def get(self, request: HttpRequest, pk):
#         pass

# class BlogCreateView(views.View):
#     # login_url = "/authen/"
#     # permission_required = ["blogs.add_blog"]
    
#     def get(self, request: HttpRequest):
#         pass
    
#     def post(self, request: HttpRequest):
#         pass
            

# class BlogEditView(views.View):
#     # login_url = "/authen/"
#     # permission_required = ["blogs.change_blog"]
    
#     def post(self, request: HttpRequest, pk):
#        pass
        
        
# class BlogDeleteView(views.View):
#     # login_url = "/authen/"
#     # permission_required = ["blogs.delete_blog"]
    
# # def get(self, request: HttpRequest, pk):    
# #         pass
        