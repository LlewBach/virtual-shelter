from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='profile'),
    path('apply-role-change/', views.apply_for_role_change, name='apply_role_change'),
]