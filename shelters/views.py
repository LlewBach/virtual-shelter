from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Shelter
from .forms import ShelterForm


@login_required
def profile(request, id):
    try:
        shelter = Shelter.objects.get(id=id)
    except Shelter.DoesNotExist:
        return render(request, 'shelters/shelter.html')
    
    animals = shelter.animals.all()
    
    return render(request, 'shelters/shelter.html', {'shelter': shelter, 'animals': animals})


@login_required
def edit_shelter(request, id):
    try:
        shelter = Shelter.objects.get(id=id)
    except Shelter.DoesNotExist:
        return redirect('shelter_profile')
    
    if request.method == 'POST':
        form = ShelterForm(request.POST, request.FILES, instance=shelter)
        if form.is_valid():
            form.save()
            return redirect('shelter_profile', id=shelter.id)
    else:
        form = ShelterForm(instance=shelter)
    
    return render(request, 'shelters/edit_shelter.html', {'form': form, 'shelter': shelter})


@login_required
def delete_shelter(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        return redirect('home')
    else:
        return render(request, 'shelters/shelter.html')


def view_shelters(request):
    shelters = Shelter.objects.all()
    return render(request, 'shelters/view_shelters.html', {'shelters': shelters})