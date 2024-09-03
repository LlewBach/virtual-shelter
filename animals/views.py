from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Animal
from .forms import AnimalForm
from shelters.models import Shelter

@login_required
def add_animal(request):
    try:
        shelter = Shelter.objects.get(admin=request.user)
    except Shelter.DoesNotExist:
        return redirect('my_shelter')

    if request.method == 'POST':
        form = AnimalForm(request.POST)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.shelter = shelter
            animal.save()
            return redirect('my_shelter')
    else:
        form = AnimalForm()
    
    return render(request, 'animals/add_animal.html', {'form': form})


def profile(request, id):
    try:
        animal = Animal.objects.get(id=id)
    except Animal.DoesNotExist:
        return redirect('home')

    return render(request, 'animals/profile.html', {'animal': animal})


@login_required
def edit_profile(request, id):
    animal = get_object_or_404(Animal, id=id)
    # Check for animal shelter's admin
    if animal.shelter.admin != request.user:
        return redirect('home')

    if request.method == 'POST':
        form = AnimalForm(request.POST, instance=animal)
        if form.is_valid():
            form.save()
            return redirect('animal_profile', id=animal.id)
    else:
        form = AnimalForm(instance=animal)

    return render(request, 'animals/edit_profile.html', {'form': form, 'animal': animal})


@login_required
def delete_profile(request, id):
    animal = get_object_or_404(Animal, id=id)
    if animal.shelter.admin != request.user:
        return redirect('profile')
    
    if request.method == 'POST':
        animal.delete()

    return redirect('home')


def view_animals(request):
    animals = Animal.objects.all()
    return render(request, 'animals/view_animals.html', {'animals': animals})