from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .models import Shelter
from .forms import ShelterForm


@login_required
def profile(request, id):
    """
    Renders the profile page for a specific shelter by its ID.
    If the shelter does not exist, redirects the user with an error message.
    Displays the shelter details and all associated animals.
    """
    try:
        shelter = Shelter.objects.get(id=id)
    except Shelter.DoesNotExist:
        messages.error(
            request, "The shelter you are looking for does not exist."
        )
        return redirect('view_shelters')

    animals = shelter.animals.all()

    return render(
        request,
        'shelters/shelter.html',
        {'shelter': shelter, 'animals': animals}
    )


@login_required
def edit_shelter(request, id):
    """
    View for editing an existing shelter. Loads the shelter by ID.
    Displays a form pre-filled with the shelter's current data.
    Handles POST requests to update shelter information if the form is valid.
    If the shelter does not exist, redirects with an error message.
    """
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

    return render(
        request,
        'shelters/edit_shelter.html',
        {'form': form, 'shelter': shelter}
    )


@login_required
def delete_shelter(request):
    """
    Handles the deletion of the user's shelter and account.
    Deletes the user's account and logs them out on a successful POST request.
    If there's an error during deletion, an error message is shown, and the
    user is redirected to the shelter profile.
    """
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
    """
    Renders a view displaying all shelters.

    Retrieves all Shelter objects and passes them to the 'view_shelters'
    template.
    """
    shelters = Shelter.objects.all()
    return render(
        request, 'shelters/view_shelters.html', {'shelters': shelters}
    )
