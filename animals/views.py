from django.shortcuts import render, redirect
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
