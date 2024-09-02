from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_animal, name='add_animal'),
    path('profile/<int:id>/', views.profile, name='animal_profile'),
]