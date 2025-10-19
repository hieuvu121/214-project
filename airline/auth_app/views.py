from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import View
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserLoginForm
from .models import UserProfile

class LoginView(View):
    template_name = 'auth/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = UserLoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        return render(request, self.template_name, {'form': form})

class RegisterView(View):
    template_name = 'auth/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Account created successfully! Welcome, {user.first_name}!')
                return redirect('home')
        return render(request, self.template_name, {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'auth/profile.html', {'user_profile': user_profile})