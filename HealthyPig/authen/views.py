from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib import messages
from django.views import View
from django.contrib.auth.forms import AuthenticationForm

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
    
# class RegisterView(View):
#     def get(self, request):
        # form = RegisterForm()
        # return render(request, 'register.html', {"form": form})
    
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