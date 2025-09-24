from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AdminUserCreationForm, EmailAuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


def create_admin_user(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Admin user {user.username} created successfully!')
            return redirect('admin_panel:login')
    else:
        form = AdminUserCreationForm()

    return render(request, 'admin_panel/create_admin.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_panel:dashboard')

    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('admin_panel:dashboard')
            else:
                messages.error(request, 'Invalid credentials or not an admin user.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmailAuthenticationForm()

    return render(request, 'admin_panel/login.html', {'form': form})


@login_required
def dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('admin_panel:login')

    total_users = User.objects.count()
    admin_users = User.objects.filter(is_staff=True).count()

    context = {
        'total_users': total_users,
        'admin_users': admin_users,
    }

    return render(request, 'admin_panel/dashboard.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('admin_panel:login')