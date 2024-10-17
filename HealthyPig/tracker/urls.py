from django.urls import path

from .views import HomePageView, MainPageView, FoodDetailListView, ExerciseDetailListView, ProgressOverviewView, StaffPageView, UserRecordView, AddMenuView, ProfileView, WeightView, EditMenuView

urlpatterns = [
    path('homepage/', HomePageView.as_view(), name="homepage"),
    path('mainpage/', MainPageView.as_view(), name="mainpage"),
    path('mainpage/fooddetail/<int:pk>/', FoodDetailListView.as_view(), name="fooddetail"),
    path('mainpage/exercisedetail/<int:pk>/', ExerciseDetailListView.as_view(), name="exercisedetail"),
    path('progress/<int:pk>/', ProgressOverviewView.as_view(), name="progresspk"),
    path('staffpage/', StaffPageView.as_view(), name='staffpage'),
    path('user_record/<int:pk>/', UserRecordView.as_view(), name='user_record'),
    path('addmenu/', AddMenuView.as_view(), name='addmenu'),
    path('editmenu/<int:food_id>/', EditMenuView.as_view(), name='editmenu'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/changeweight/', WeightView.as_view(), name='changeweight'),
]   
