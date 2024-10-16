from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('select-sprite/<int:id>/', views.select_sprite, name='select_sprite'),
    path('select-sprite/<int:id>/', views.select_sprite, name='select_sprite'),
    path('delete-sprite/<int:id>/', views.delete_sprite, name='delete_sprite'),
    path(
      'sprite/<int:sprite_id>/update-status/',
      views.update_status,
      name='update_status'
      ),
    path(
      'sprite/<int:sprite_id>/feed/',
      views.feed_sprite,
      name='feed_sprite'
      ),
]
