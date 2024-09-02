from django.urls import path
from . import views

urlpatterns = [
    path('my-shelter/', views.my_shelter, name='my_shelter'),
    path('my-shelter/edit/', views.edit_my_shelter, name='edit_my_shelter'),
    path('my-shelter/delete/', views.delete_my_shelter, name='delete_my_shelter'),
]