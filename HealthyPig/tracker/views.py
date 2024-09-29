from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
# from blogs.forms import BlogForm
from django.core.exceptions import PermissionDenied
from django import views
# from blogs.models import Blog

from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


# exercise/food ห้ามลบ เพิ่มกับแก้ได้อย่างเดียว

class HomePageView(views.View):
    # login_url = "/authen/"
    # permission_required = [".view_blog"]
    def get(self, request):
        # form = AuthenticationForm()
        return render(request, 'homepage.html')

class BlogDetailView(views.View):
    # login_url = "/authen/"
    # permission_required = ["blogs.view_blog"]
    
    def get(self, request: HttpRequest, pk):
        pass

class BlogCreateView(views.View):
    # login_url = "/authen/"
    # permission_required = ["blogs.add_blog"]
    
    def get(self, request: HttpRequest):
        pass
    
    def post(self, request: HttpRequest):
        pass
            

class BlogEditView(views.View):
    # login_url = "/authen/"
    # permission_required = ["blogs.change_blog"]
    
    def post(self, request: HttpRequest, pk):
       pass
        
        
class BlogDeleteView(views.View):
    # login_url = "/authen/"
    # permission_required = ["blogs.delete_blog"]
    
    def get(self, request: HttpRequest, pk):
        pass
        