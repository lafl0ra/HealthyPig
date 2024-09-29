from django.urls import path

# from authen.views import *
from authen.views import LoginView , LogoutView , RegisterView


urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('register/', RegisterView.as_view(), name="register")
]