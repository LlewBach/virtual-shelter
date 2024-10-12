from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import SpriteForm
from .models import Sprite
from animals.models import Animal
from profiles.models import Profile

@login_required
def dashboard(request):
    """
    Display the user's dashboard with their profile and sprites.
    Also handles messages related to payment status (success or cancel).
    """
    profile = Profile.objects.get(user=request.user)
    sprites = Sprite.objects.filter(user=request.user)
    context = {
        'profile': profile,
        'sprites': sprites
    }

    # If redirected from checkout session
    payment_status = request.GET.get('payment_status')

    if payment_status == 'success':
        messages.success(request, "Payment successful! Received 100 tokens.")
    
    elif payment_status == 'cancel':
        messages.error(request, "Payment canceled. No tokens added.")

    return render(request, 'dashboard/dashboard.html', context)


def select_sprite(request, id):
    """
    View that handles selecting and fostering a sprite for a specific animal.
    Prevents shelter admins and existing fosterers from fostering the animal.
    On successful form submission, assigns the sprite to the user and updates the animal's status.
    """
    animal = get_object_or_404(Animal, id=id)
    if request.user.profile.role == 'shelter_admin' or animal.fosterer == request.user.profile:
        messages.warning(request, "You cannot foster this animal")
        return redirect('view_animals')

    if request.method == 'POST':
        form = SpriteForm(request.POST)
        if form.is_valid():
            sprite = form.save(commit=False)
            sprite.user = request.user
            sprite.animal = animal
            breed_choice = request.POST.get('breed')
            sprite.breed = breed_choice
            colour_choice = request.POST.get('colour')
            sprite.colour = colour_choice
            sprite.url = f'{breed_choice}/{colour_choice}'
            sprite.save()

            animal.fosterer = request.user.profile
            animal.adoption_status = 'Fostered'
            animal.save()

            messages.success(request, f"'{animal.name}' fostered")
            return redirect('dashboard')
        else:
            messages.error(request, "Error fostering - Check the form")
    else:
        form = SpriteForm()

    return render(request, 'dashboard/select_sprite.html', {'form': form})


def delete_sprite(request, id):
    """
    View to delete a sprite and return the associated animal to the shelter.
    Ensures only the user who fostered the sprite can delete it.
    On success, the animal's adoption status is updated to 'Available'.
    """
    sprite = get_object_or_404(Sprite, id=id)

    if sprite.user != request.user:
        messages.error(request, "Not authorized to delete this sprite")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            animal = sprite.animal
            animal.fosterer = None
            animal.adoption_status = 'Available'
            animal.save()
            sprite.delete()
            messages.success(request, f"'{animal.name}' returned to shelter")
        except Exception as e:
            messages.error(request, f"Error removing '{animal.name}' from foster")

    return redirect('dashboard')


def update_status(request, sprite_id):
    """
    View to update the status of a sprite and return its current stats as JSON.
    Retrieves the sprite by its ID, updates its status, and returns a JSON
    response with the updated satiation, current state, time standing, and time running.
    """
    sprite = get_object_or_404(Sprite, id=sprite_id)
    sprite.update_status()
    return JsonResponse({
        'satiation': sprite.satiation,
        'current_state': sprite.current_state,
        'time_standing': sprite.time_standing,
        'time_running': sprite.time_running,
    })


def feed_sprite(request, sprite_id):
    """
    View to feed a sprite. Deducts 1 token from the user's profile if they have enough tokens,
    increases the sprite's satiation by 5 (capped at 100), and returns a JSON response 
    with the updated satiation and token count. Returns an error if the user has insufficient tokens.
    """
    sprite = get_object_or_404(Sprite, id=sprite_id)
    profile = request.user.profile

    token_cost = 1

    # Check if the user has enough tokens
    if profile.tokens < token_cost:
        return JsonResponse({
            'success': False,
            'error': 'Not enough tokens to feed the sprite.'
        }, status=400)
    
    profile.tokens -= token_cost
    profile.save()

    sprite.satiation = min(sprite.satiation + 5, 100)
    sprite.save()

    return JsonResponse({
        'success': True,
        'satiation': sprite.satiation,
        'tokens': profile.tokens
    })

