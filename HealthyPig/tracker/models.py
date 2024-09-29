from django.db import models
from django.contrib.auth.models import User
 
class UserProfile(models.Model):
    birth_date = models.DateField()
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    gender = models.CharField(max_length=5,choices=GENDER_CHOICES)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.0) #เพิ่มเข้ามานะ
    BMI = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.0)
    BMR = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.0)
    TDEE = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.0)
    goal_amount_day = models.IntegerField(null=False)
    goal_weight = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # editable = False => ทำให้ไม่แสดงใน form
    # def __str__(self):
    #     return self.user.username
    def __str__(self):
        return f"{self.user.username}'s Profile"

class User_Info_Record(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    datetime_update = models.DateTimeField(auto_now_add=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.0)
    
class FoodType(models.Model):
    name = models.CharField(max_length=150, null=False)

class Food(models.Model):
    name = models.CharField(max_length=150, null=False)
    calories = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.0)
    description = models.TextField()
    quantity_in_grams = models.DecimalField(max_digits=10, decimal_places=2)
    ingredients = models.ManyToManyField('self', symmetrical=False, related_name='included_in')
    # staff = models.ForeignKey(User, on_delete=models.CASCADE) ไม่รู้ว่าต้องมีไหม หรือใช้รวมกับ user ด้านล่างได้เลย
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_type = models.ManyToManyField(FoodType)

class FoodRecord(models.Model):
    foodrecord = models.ForeignKey(Food, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    datetime_record = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.0)
    sum_calories = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.0)

class Exercise(models.Model): # EXERCISE ห้ามลบ แก้ไขกับเพิ่มได้อยางเดียว
    staff = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=20, null=False)
    calories_burned_per_min = models.IntegerField(null=False)
    description = models.TextField()

class ExerciseRecord(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, null=False) # ห้ามลบ exercise !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    datetime_record = models.DateTimeField(auto_now_add=True) # auto_now_add จะบันทึกเวลาที่สร้างวัตถุครั้งแรก
    amount= models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.0)
    sum_calories = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.0)