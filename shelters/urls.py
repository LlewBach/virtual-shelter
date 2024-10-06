from django.urls import path
from . import views

urlpatterns = [
    path('profile/<int:id>/', views.profile, name='shelter_profile'),
    path('profile/edit/<int:id>/', views.edit_shelter, name='edit_shelter'),
    path('profile/delete/', views.delete_shelter, name='delete_shelter'),
    path('', views.view_shelters, name='view_shelters'),
]