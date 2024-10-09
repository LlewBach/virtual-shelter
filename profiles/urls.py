from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='profile'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('delete/', views.delete_profile, name='delete_profile'),
    path('apply-role-change/', views.apply_for_role_change, name='apply_role_change'),
    path('tokens/', views.tokens, name='tokens'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
]