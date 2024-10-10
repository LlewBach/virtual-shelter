from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Shelter
from .forms import ShelterForm


@login_required
def profile(request, id):
    try:
        shelter = Shelter.objects.get(id=id)
    except Shelter.DoesNotExist:
        messages.error(request, "The shelter you are looking for does not exist.")
        return redirect('view_shelters')
    
    animals = shelter.animals.all()
    
    return render(request, 'shelters/shelter.html', {'shelter': shelter, 'animals': animals})


@login_required
def edit_shelter(request, id):
    try:
        shelter = Shelter.objects.get(id=id)
    except Shelter.DoesNotExist:
        messages.error(request, "Shelter not found")
        return redirect('view_shelters')
    
    if request.method == 'POST':
        form = ShelterForm(request.POST, request.FILES, instance=shelter)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{shelter.name}' updated")
            return redirect('shelter_profile', id=shelter.id)
        else:
            messages.error(request, "Error updating shelter - Check the form")
    else:
        form = ShelterForm(instance=shelter)
    
    return render(request, 'shelters/edit_shelter.html', {'form': form, 'shelter': shelter})


@login_required
def delete_shelter(request):
    if request.method == 'POST':
        try:
            user = request.user
            user.delete()
            logout(request)
            messages.success(request, "Account deleted")
            return redirect('home')
        except Exception as e:
            messages.error(request, "Error deleting account")
            return redirect('shelter_profile', id=user.shelter.id)


def view_shelters(request):
    shelters = Shelter.objects.all()
    return render(request, 'shelters/view_shelters.html', {'shelters': shelters})