from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import RoleChangeRequestForm

def profile(request):
    user_profile = Profile.objects.get(user=request.user)
    return render(request, 'profiles/profile.html', {'role': user_profile.role})

# Create your views here.
@login_required
def apply_for_role_change(request):
    if request.method == 'POST':
        form = RoleChangeRequestForm(request.POST)
        if form.is_valid():
            role_request = form.save(commit=False)
            role_request.user = request.user
            role_request.save()
            return redirect('dashboard')  # Redirect to the dashboard or a success page
    else:
        form = RoleChangeRequestForm()
    return render(request, 'profiles/apply_role_change.html', {'form': form})