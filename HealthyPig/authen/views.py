from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from authen.forms import RegisterForm
from django.db import transaction
from datetime import datetime
from tracker.models import UserProfile, User_Info_Record


class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {"form": form})
    
    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request,user)
            return redirect('blog-list')
        return render(request,'login.html', {"form":form})

class LogoutView(View):
    
    def get(self, request):
        logout(request)
        return redirect('login')

class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'register.html', {"form": form})
    

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(55555555)
            birth_date = form.cleaned_data['birth_date']
            gender = form.cleaned_data['gender']
            height = float(form.cleaned_data['height'])
            weight = float(form.cleaned_data['weight'])
            goal_weight = float(form.cleaned_data['goal_weight'])
            

            today = datetime.today() 
            age = today.year - birth_date.year  
            if (today.month, today.day) < (birth_date.month, birth_date.day): 
                age -= 1
                

            BMI = (weight) / (height/100)**2
            

            BMR = 0
            if gender == "F":
                BMR = 665 + (9.6 * weight) +  (1.8 * height) - (4.7 * age)
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
            if  goal_weight_per_week == 'easy':
                goal_amount_day = (goal_weight / 0.25) * 7
            elif  goal_weight_per_week == 'recommend':
                goal_amount_day = (goal_weight / 0.33) * 7
            elif  goal_weight_per_week == 'normal':
                goal_amount_day = (goal_weight / 0.5) * 7
            elif  goal_weight_per_week == 'hard':
                goal_amount_day = (goal_weight / 1) * 7

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
            new_userprofile .save()
            print(1)
            datetime_update = datetime.today()
            new_user_info_record = User_Info_Record(
                datetime_update=datetime_update,
                weight=weight,
                user=new_userprofile,
            )
            new_user_info_record.save()
            print(2)
            return redirect('login')
        else:
            print(form.errors)
            return render(request, "register.html", {"form": form})
    



        #อันนี้ Example อาจารย์ week 11
        #      Em = Employee.objects.create(first_name = form.cleaned_data.get("first_name"),
        #                                  last_name = form.cleaned_data.get("last_name"),
        #                               gender = form.cleaned_data.get("gender"),
        #                                   birth_date = form.cleaned_data.get("birth_date"),
        #                                   hire_date = form.cleaned_data.get("hire_date"),
        #                                   salary = form.cleaned_data.get("salary"),
        #                                   position_id = (form.cleaned_data.get("position")).id)
            
        #     Ad = EmployeeAddress.objects.create(location = form.cleaned_data.get("location"),
        #                                   district = form.cleaned_data.get("district"),
        #                                   province = form.cleaned_data.get("province"),
        #                                   postal_code = form.cleaned_data.get("postal_code"),
        #                                   employee = Em)
        #     return redirect("employee")
        # else:
        #     return render(request, "employee_form.html", {"form": form})
    

    # class Employee_FormView(View):

    # def get(self, request):
    #     form = EmployeeForm()  # สร้างฟอร์มใหม่สำหรับ GET
    #     return render(request, "employee_form.html", {"form": form})
    
    # @transaction.atomic
    # def post(self, request):
    #     form = EmployeeForm(request.POST)  # ตรวจสอบคำขอแบบ POST
    #     if form.is_valid():
    #         # บันทึกข้อมูลพนักงานในตาราง Employee
    #         first_name = form.cleaned_data["first_name"]
    #         last_name = form.cleaned_data["last_name"]
    #         gender = form.cleaned_data["gender"]
    #         birth_date = form.cleaned_data["birth_date"]
    #         hire_date = form.cleaned_data["hire_date"]
    #         salary = form.cleaned_data["salary"]
    #         position = form.cleaned_data["position"]  # position จาก ForeignKey

    #         # สร้าง employee record
    #         new_employee = Employee.objects.create(
    #             first_name=first_name,
    #             last_name=last_name,
    #             gender=gender,
    #             birth_date=birth_date,
    #             hire_date=hire_date,
    #             salary=salary,
    #             position_id=position.id  # สามารถใช้ position ตรงๆ ได้เลย
    #         )

    #         # บันทึกข้อมูลที่อยู่พนักงานในตาราง EmployeeAddress
    #         location = form.cleaned_data["location"]
    #         district = form.cleaned_data["district"]
    #         province = form.cleaned_data["province"]
    #         postal_code = form.cleaned_data["postal_code"]
            
    #         EmployeeAddress.objects.create(
    #             employee=new_employee, #PK
    #             location=location, 
    #             district=district, 
    #             province=province, 
    #             postal_code=postal_code
    #         )

    #         return redirect("employee")  # เปลี่ยนเส้นทางไปยังหน้า employee

    #     # ถ้ามีข้อผิดพลาดในฟอร์ม ให้แสดงฟอร์มพร้อมข้อผิดพลาดอีกครั้ง
    #     return render(request, "employee_form.html", {"form": form})
    
    # def sign_up(request):
    # if request.method == 'GET':
    #     form = RegisterForm()
    #     return render(request, 'users/register.html', { 'form': form})  
    
    # def post(self, request):
    #     form = AuthenticationForm(data=request.POST)
    #     if form.is_valid():
    #         user = form.get_user() 
    #         login(request,user)
    #         return redirect('blog-list')
    #     return render(request,'register.html', {"form":form})
    
# class BlogCreateView(LoginRequiredMixin, PermissionRequiredMixin, views.View):
    
#     def get(self, request: HttpRequest):
#         form = BlogForm()
#         context = {
#             "form": form
#         }
#         return render(request, 'blog_create.html', context)
    
#     def post(self, request: HttpRequest):
#         form = BlogForm(request.POST)
        
#         if form.is_valid():
#             blog = form.save(commit=False)
#             blog.author = request.user
#             blog.save()
#             form.save_m2m()
#             return redirect('blog-list')
#         else:
#             return render(request, "blog_create.html", {"form": form})