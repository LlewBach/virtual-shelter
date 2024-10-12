from django.shortcuts import render


def index(request):
    """
    View for rendering the home page (index). Renders the 'home/index.html' template.
    """
    return render(request, 'home/index.html')