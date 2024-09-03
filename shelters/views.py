from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Shelter
from .forms import ShelterForm


@login_required
def my_shelter(request):
    try:
        my_shelter = Shelter.objects.get(admin=request.user)
    except Shelter.DoesNotExist:
        return render(request, 'shelters/my_shelter.html')
    
    animals = my_shelter.animals.all()
    
    return render(request, 'shelters/my_shelter.html', {'my_shelter': my_shelter, 'animals': animals})


@login_required
def edit_my_shelter(request):
    try:
        my_shelter = Shelter.objects.get(admin=request.user)
    except Shelter.DoesNotExist:
        return redirect('my_shelter')
    
    if request.method == 'POST':
        form = ShelterForm(request.POST, instance=my_shelter)
        if form.is_valid():
            form.save()
            return redirect('my_shelter')
    else:
        form = ShelterForm(instance=my_shelter)
    
    return render(request, 'shelters/edit_my_shelter.html', {'form': form})


@login_required
def delete_my_shelter(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        return redirect('home')
    else:
        return render(request, 'shelters/my_shelter.html')


def view_shelters(request):
    shelters = Shelter.objects.all()
    return render(request, 'shelters/view_shelters.html', {'shelters': shelters})