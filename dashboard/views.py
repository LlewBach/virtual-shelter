from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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
            sprite.sprite_sheet = request.POST.get('sprite_sheet')
            sprite.save()
            return redirect('dashboard')
    else:
        form = SpriteForm()

    return render(request, 'dashboard/select_sprite.html', {'form': form})