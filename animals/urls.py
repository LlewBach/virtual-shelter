from django.urls import path
from . import views


urlpatterns = [
    path('add/', views.add_animal, name='add_animal'),
    path('profile/<int:id>/', views.profile, name='animal_profile'),
    path(
      'edit-profile/<int:id>/',
      views.edit_profile,
      name='edit_animal_profile'
      ),
    path(
      'delete-profile/<int:id>/',
      views.delete_profile,
      name='delete_animal_profile'
      ),
    path('', views.view_animals, name='view_animals'),
    path('add-update/<int:id>/', views.add_update, name='add_update'),
    path('edit-update/<int:id>/', views.edit_update, name='edit_update'),
    path('delete-update/<int:id>/', views.delete_update, name='delete_update'),
]
