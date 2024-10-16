import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Profile
from .forms import ProfileForm, RoleChangeRequestForm


@login_required
def profile(request):
    """
    View to display user's profile and associated animals.
    """
    user_profile = Profile.objects.get(user=request.user)
    animals = user_profile.animals.all()
    return render(
        request,
        'profiles/profile.html',
        {'profile': user_profile, 'animals': animals}
    )


@login_required
def edit_profile(request):
    """
    View for editing the user's profile.
    """
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found")
        return redirect('home')

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile saved")
            return redirect('profile')
        else:
            messages.error(request, "Error saving - Check the form")
    else:
        form = ProfileForm(instance=user_profile)

    return render(request, 'profiles/edit_profile.html', {'form': form})


@login_required
def delete_profile(request):
    """
    View for deleting the user's account.
    """
    if request.method == 'POST':
        try:
            user = request.user
            user.delete()
            messages.success(request, "Profile deleted")
            logout(request)
            return redirect('home')
        except Exception as e:
            messages.error(request, "Error deleting profile")
            return redirect('profile')
    else:
        return render(request, 'profiles/profile.html')


@login_required
def apply_for_role_change(request):
    """
    View for submitting a role change request to become a shelter admin.
    """
    if request.method == 'POST':
        form = RoleChangeRequestForm(request.POST)
        if form.is_valid():
            role_request = form.save(commit=False)
            role_request.user = request.user
            role_request.save()
            messages.success(request, "Request submitted")
            return redirect('dashboard')
        else:
            messages.error(request, "Error with request")
    else:
        form = RoleChangeRequestForm()
    return render(request, 'profiles/apply_role_change.html', {'form': form})


@login_required
def tokens(request):
    """
    View for displaying pre-checkout tokens page.
    """
    profile = Profile.objects.get(user=request.user)
    return render(request, 'profiles/tokens.html', {'profile': profile})


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(request):
    """
    View for the Stripe checkout session to purchase virtual tokens.
    """
    token_cost = 499
    domain = request.build_absolute_uri('/').strip('/')

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'gbp',
                        'product_data': {
                            'name': '100 Virtual Shelter Tokens',
                        },
                        'unit_amount': token_cost,
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url=f'{domain}/dashboard/?payment_status=success',
            cancel_url=f'{domain}/dashboard/?payment_status=cancel',
            metadata={
                'user_id': request.user.id
            }
        )
        return redirect(checkout_session.url, code=302)
    except Exception as e:
        print("Stripe session creation error:", e)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def stripe_webhook(request):
    """
    View for the stripe webhook to update user's token count if payment
    successful.
    """
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WH_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return JsonResponse({'status': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'status': 'Invalid signature'}, status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Get the user ID from the session metadata
        user_id = session.get('metadata', {}).get('user_id')

        if user_id:
            try:
                profile = Profile.objects.get(user_id=user_id)
                # Add tokens to user's profile based on the payment
                profile.tokens += 100
                profile.save()
            except Profile.DoesNotExist:
                return JsonResponse(
                    {'status': 'User profile not found'},
                    status=404
                )

    return JsonResponse({'status': 'success'}, status=200)
