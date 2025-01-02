from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views import View
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import RegistrationForm 
from shop.models import Cart


class LoginView(View):

    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {"form": form})

    def post(self, request):
        
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request, user)
            return redirect('homepage')
        else:
            return render(request, 'login.html', {"form": form})


class LogoutView(View):

    def get(self, request):
        logout(request)
        # messages.success(request, "You have been logged out.")
        return redirect('login')
    
class RegisterView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'register.html', {"form": form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save the user yet
            user.set_password(form.cleaned_data['password1'])  # Set the password
            user.save()  # Now save the user to the database
            
            # Create a new cart for the user
            Cart.objects.create(user=user)  # สร้างตะกร้าสำหรับผู้ใช้ใหม่
            
            login(request, user)  # Log the user in after registration
            return redirect('homepage')  # Redirect to the login page after successful registration
        else:
            return render(request, 'register.html', {"form": form})