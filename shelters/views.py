from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Shelter


@login_required
def my_shelter(request):
    try:
        my_shelter = Shelter.objects.get(admin=request.user)
    except Shelter.DoesNotExist:
        return render(request, 'shelters/my_shelter.html')
    
    return render(request, 'shelters/my_shelter.html', {'my_shelter': my_shelter})
