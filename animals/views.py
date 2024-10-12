from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Animal, Update
from .forms import AnimalForm, UpdateForm
from shelters.models import Shelter

@login_required
def add_animal(request):
    """
    Allows a shelter admin to add a new animal to their shelter.

    If the user is not a shelter admin, they are redirected with an error message.
    If a valid form is submitted, the animal is saved and the user is redirected to the shelter profile.
    If the form is invalid, an error message is shown and the form is re-rendered.
    """
    try:
        shelter = Shelter.objects.get(admin=request.user)
    except Shelter.DoesNotExist:
        messages.error(request, "You aren't a shelter admin")
        return redirect('home')

    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.shelter = shelter
            animal.save()
            messages.success(request, f"Animal '{animal.name}' added")
            return redirect('shelter_profile', shelter.id)
        else:
            messages.error(request, "Error adding animal. Check form")
    else:
        form = AnimalForm()
    
    return render(request, 'animals/add_animal.html', {'form': form})


def profile(request, id):
    """
    Displays the profile page for a specific animal.

    Attempts to retrieve the animal by its ID. If the animal does not exist,
    an error message is shown and the user is redirected to the homepage.
    Otherwise, the animal's profile page is rendered.
    """
    try:
        animal = Animal.objects.get(id=id)
    except Animal.DoesNotExist:
        messages.error(request, "Animal not found")
        return redirect('home')

    return render(request, 'animals/profile.html', {'animal': animal})


@login_required
def edit_profile(request, id):
    """
    Allows the shelter admin to edit an animal's profile.

    Retrieves the animal by its ID and checks if the logged-in user is the admin of the animal's shelter.
    If not, an error message is shown and the user is redirected to the homepage.
    If the form is valid on POST, the animal is updated and the user is redirected to the animal's profile.
    If the form is invalid, an error message is shown and the form is re-rendered.
    """
    animal = get_object_or_404(Animal, id=id)
    if animal.shelter.admin != request.user:
        messages.error(request, "Only shelter admin can edit animal")
        return redirect('home')

    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            form.save()
            messages.success(request, f"Animal saved")
            return redirect('animal_profile', id=animal.id)
        else:
            messages.error(request, "Error saving animal - Check the form")
    else:
        form = AnimalForm(instance=animal)

    return render(request, 'animals/edit_profile.html', {'form': form, 'animal': animal})


@login_required
def delete_profile(request, id):
    """
    Allows the shelter admin to delete an animal's profile.

    Retrieves the animal by its ID and checks if the logged-in user is the admin of the animal's shelter.
    If not, an error message is shown and the user is redirected to their profile page.
    If a POST request is made and the animal is successfully deleted, a success message is shown.
    If the deletion fails, an error message is displayed and the user is redirected to the shelter profile.
    """
    animal = get_object_or_404(Animal, id=id)
    if animal.shelter.admin != request.user:
        messages.error(request, "Only shelter admin can delete animal")
        return redirect('profile')
    
    if request.method == 'POST':
        try:
            animal.delete()
            messages.success(request, f"Animal '{animal.name}' deleted.")
        except:
            messages.error(request, "Error deleting animal")
            return redirect('shelter_profile', id=animal.shelter.id)

    return redirect('home')


def view_animals(request):
    """
    Displays a list of all animals.

    Retrieves all Animal objects and renders them on the 'view_animals' template.
    """
    animals = Animal.objects.all()
    return render(request, 'animals/view_animals.html', {'animals': animals})


@login_required
def add_update(request, id):
    """
    Allows the shelter admin to add an update for a specific animal.

    Retrieves the animal by its ID and checks if the logged-in user is the admin of the animal's shelter.
    If not, an error message is shown, and the user is redirected to the animal's profile.
    On a valid form submission, the update is saved and linked to the animal, and the user is redirected to the animal's profile.
    If the form is invalid, an error message is displayed and the form is re-rendered.
    """
    animal = get_object_or_404(Animal, id=id)

    if animal.shelter.admin != request.user:
        messages.error(request, "Only shelter admin can add update")
        return redirect('animal_profile', id=animal.id)

    if request.method == 'POST':
        form = UpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.animal = animal
            update.save()
            messages.success(request, f"Update added for '{animal.name}'.")
            return redirect('animal_profile', id=animal.id)
        else:
            messages.error(request, "Error adding update - Check the form")
    else:
        form = UpdateForm()

    return render(request, 'animals/add_update.html', {'form': form, 'animal': animal})


@login_required
def edit_update(request, id):
    """
    Allows the shelter admin to edit an existing update for an animal.

    Retrieves the update by its ID and checks if the logged-in user is the admin of the animal's shelter.
    If not, an error message is shown, and the user is redirected to the animal's profile.
    If the form is valid on POST, the update is saved and the user is redirected to the animal's profile.
    If the form is invalid, an error message is displayed and the form is re-rendered with errors.
    """
    update = get_object_or_404(Update, id=id)

    if update.animal.shelter.admin != request.user:
        messages.error(request, "Only shelter admin can edit this update")
        return redirect('animal_profile', id=update.animal.id)

    if request.method == 'POST':
        form = UpdateForm(request.POST, instance=update)
        if form.is_valid():
            form.save()
            messages.success(request, f"Update for '{update.animal.name}' edited")
            return redirect('animal_profile', id=update.animal.id)
        else:
            messages.error(request, "Error editing update - Check the form")
    else:
        form = UpdateForm(instance=update)

    return render(request, 'animals/edit_update.html', {'form': form, 'update': update})


@login_required
def delete_update(request, id):
    """
    Allows the shelter admin to delete an update for an animal.

    Retrieves the update by its ID and checks if the logged-in user is the admin of the animal's shelter.
    If not, an error message is shown, and the user is redirected to the animal's profile.
    If the request is a POST and the update is successfully deleted, a success message is shown.
    If an error occurs during deletion, an error message is displayed.
    """
    update = get_object_or_404(Update, id=id)

    if update.animal.shelter.admin != request.user:
        messages.error(request, "Only shelter admin can delete this update")
        return redirect('animal_profile', id=update.animal.id)

    if request.method == 'POST':
        try:
            update.delete()
            messages.success(request, f"Update for '{update.animal.name}' deleted")
        except Exception as e:
            messages.error(request, "Error deleting update")
    
    return redirect('animal_profile', id=update.animal.id)