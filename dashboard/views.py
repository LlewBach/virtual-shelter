from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import SpriteForm
from .models import Sprite
from animals.models import Animal

@login_required
def dashboard(request):
    sprites = Sprite.objects.filter(user=request.user)
    context = {
        'sprites': sprites
    }

    return render(request, 'dashboard/dashboard.html', context)


def select_sprite(request, id):
    if request.method == 'POST':
        form = SpriteForm(request.POST)
        if form.is_valid():
            sprite = form.save(commit=False)
            sprite.user = request.user
            animal = get_object_or_404(Animal, id=id)
            sprite.animal = animal
            breed_choice = request.POST.get('breed')
            sprite.breed = breed_choice
            colour_choice = request.POST.get('colour')
            sprite.colour = colour_choice
            sprite.url = f'{breed_choice}/{colour_choice}'
            sprite.save()
            return redirect('dashboard')
    else:
        form = SpriteForm()

    return render(request, 'dashboard/select_sprite.html', {'form': form})


def delete_sprite(request, id):
    sprite = get_object_or_404(Sprite, id=id)
    
    # needs to test if owner

    if request.method == 'POST':
        sprite.delete()

    return redirect('dashboard')


def update_status(request, sprite_id):
    sprite = get_object_or_404(Sprite, id=sprite_id)
    sprite.update_status()
    return JsonResponse({'satiation': sprite.satiation})


def feed_sprite(request, sprite_id):
    sprite = get_object_or_404(Sprite, id=sprite_id)

    sprite.satiation = min(sprite.satiation + 2, 100)
    sprite.save()

    return JsonResponse({
        'success': True,
        'satiation': sprite.satiation
    })

