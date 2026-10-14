from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import RegistrationForm, LoginForm, ProfileUpdateForm

def register_view(request):
    """
    User registration view with validation and automatic login.
    """
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatic login after signup
            login(request, user)
            messages.success(request, f"Welcome to Vcart, {user.first_name or user.username}! Your account has been created.")
            
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=settings.ALLOWED_HOSTS):
                return redirect(next_url)
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, "Please review the errors below and try again.")
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'next': next_url,
    })


def login_view(request):
    """
    User login view supporting ?next= parameter redirect.
    Staff/Admin users are directed to the operations dashboard by default.
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard:home')
        return redirect(settings.LOGIN_REDIRECT_URL)

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            display_name = user.get_full_name() or user.username
            messages.success(request, f"Welcome back, {display_name}!")

            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=settings.ALLOWED_HOSTS):
                return redirect(next_url)
            if user.is_staff:
                return redirect('dashboard:home')
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': next_url,
    })


def logout_view(request):
    """
    Logout view strictly executed via POST.
    If accessed via GET, provides a confirmation prompt submitting POST.
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, "You have been successfully signed out.")
        return redirect(settings.LOGOUT_REDIRECT_URL)
    
    # If unauthenticated GET, redirect to home
    if not request.user.is_authenticated:
        return redirect(settings.LOGOUT_REDIRECT_URL)
        
    return render(request, 'accounts/logout_confirm.html')


@login_required
def profile_view(request):
    """
    Protected Account/Profile page.
    Displays username, email, full name, date joined,
    and a form to edit first name, last name, and email.
    """
    user = request.user

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile information has been updated successfully.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors in the profile form.")
    else:
        form = ProfileUpdateForm(instance=user)

    context = {
        'user': user,
        'form': form,
        'full_name': user.get_full_name() or "Not set",
        'date_joined': user.date_joined,
    }
    return render(request, 'accounts/profile.html', context)
