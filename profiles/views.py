from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import RoleChangeRequestForm

@login_required
def profile(request):
    user_profile = Profile.objects.get(user=request.user)
    return render(request, 'profiles/profile.html', {'profile': user_profile})


@login_required
def apply_for_role_change(request):
    if request.method == 'POST':
        form = RoleChangeRequestForm(request.POST)
        if form.is_valid():
            role_request = form.save(commit=False)
            role_request.user = request.user
            role_request.save()
            return redirect('dashboard')
    else:
        form = RoleChangeRequestForm()
    return render(request, 'profiles/apply_role_change.html', {'form': form})