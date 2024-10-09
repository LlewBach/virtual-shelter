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
    animal = get_object_or_404(Animal, id=id)
    # if request.user.profile.role == 'shelter_admin' or animal.fosterer == request.user.profile:
    #     return redirect('view_animals')

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
            return redirect('dashboard')
    else:
        form = SpriteForm()

    return render(request, 'dashboard/select_sprite.html', {'form': form})


def delete_sprite(request, id):
    sprite = get_object_or_404(Sprite, id=id)

    if sprite.user != request.user:
        return redirect('dashboard')

    if request.method == 'POST':
        animal = sprite.animal
        animal.fosterer = None
        animal.adoption_status = 'Available'
        animal.save()
        sprite.delete()

    return redirect('dashboard')


def update_status(request, sprite_id):
    sprite = get_object_or_404(Sprite, id=sprite_id)
    sprite.update_status()
    return JsonResponse({
        'satiation': sprite.satiation,
        'current_state': sprite.current_state,
        'time_standing': sprite.time_standing,
        'time_running': sprite.time_running,
    })


def feed_sprite(request, sprite_id):
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

