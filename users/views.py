from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, JobSeekerProfileForm, EmployerProfileForm, UserUpdateForm
from .models import JobSeekerProfile, EmployerProfile

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    # Get or create profiles based on user type
    if request.user.user_type == 'job_seeker':
        profile_obj, created = JobSeekerProfile.objects.get_or_create(user=request.user)
    else:
        profile_obj, created = EmployerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        
        if request.user.user_type == 'job_seeker':
            profile_form = JobSeekerProfileForm(request.POST, request.FILES, instance=profile_obj)
        else:
            profile_form = EmployerProfileForm(request.POST, request.FILES, instance=profile_obj)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        if request.user.user_type == 'job_seeker':
            profile_form = JobSeekerProfileForm(instance=profile_obj)
        else:
            profile_form = EmployerProfileForm(instance=profile_obj)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'users/profile.html', context)