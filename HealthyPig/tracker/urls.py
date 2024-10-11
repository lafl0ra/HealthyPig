from django.urls import path

from .views import HomePageView, MainPageView, FoodDetailListView, ExerciseDetailListView, ProgressOverviewView

urlpatterns = [
    path('', HomePageView.as_view(), name="homepage"),
    path('mainpage/', MainPageView.as_view(), name="mainpage"),
    path('mainpage/fooddetail/<int:pk>/', FoodDetailListView.as_view(), name="fooddetail"),
    path('mainpage/exercisedetail/<int:pk>/', ExerciseDetailListView.as_view(), name="exercisedetail"),
    path('progress/', ProgressOverviewView.as_view(), name="progress"),
]
