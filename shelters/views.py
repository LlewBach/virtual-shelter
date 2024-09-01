from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Shelter
from .forms import ShelterForm


@login_required
def my_shelter(request):
    try:
        my_shelter = Shelter.objects.get(admin=request.user)
    except Shelter.DoesNotExist:
        return render(request, 'shelters/my_shelter.html')
    
    return render(request, 'shelters/my_shelter.html', {'my_shelter': my_shelter})


@login_required
def edit_my_shelter(request):
    try:
        my_shelter = Shelter.objects.get(admin=request.user)
    except Shelter.DoesNotExist:
        return redirect('my_shelter')
    
    if request.method == 'POST':
        form = ShelterForm(request.POST, instance=my_shelter)
        if form.is_valid():
            form.save()
            return redirect('my_shelter')
    else:
        form = ShelterForm(instance=my_shelter)
    
    return render(request, 'shelters/edit_my_shelter.html', {'form': form})

