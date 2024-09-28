from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='profile'),
    path('apply-role-change/', views.apply_for_role_change, name='apply_role_change'),
    path('tokens/', views.tokens, name='tokens'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('tokens/success/', views.success_view, name='success_view'),
    path('tokens/cancel/', views.cancel_view, name='cancel_view'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
]