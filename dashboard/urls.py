from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('select-sprite/<int:id>/', views.select_sprite, name='select_sprite'),
]