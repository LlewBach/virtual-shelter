from django.urls import path
from . import views

urlpatterns = [
    path('my-shelter/', views.my_shelter, name='my_shelter'),
]