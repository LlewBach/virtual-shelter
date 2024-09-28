import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .models import Profile
from .forms import RoleChangeRequestForm


@login_required
def profile(request):
    user_profile = Profile.objects.get(user=request.user)
    return render(request, 'profiles/profile.html', {'profile': user_profile})


@login_required
def apply_for_role_change(request):
    if request.method == 'POST':
        form = RoleChangeRequestForm(request.POST)
        if form.is_valid():
            role_request = form.save(commit=False)
            role_request.user = request.user
            role_request.save()
            return redirect('dashboard')
    else:
        form = RoleChangeRequestForm()
    return render(request, 'profiles/apply_role_change.html', {'form': form})


@login_required
def tokens(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'profiles/tokens.html', {'profile': profile})


stripe.api_key = settings.STRIPE_SECRET_KEY
def create_checkout_session(request):
    token_cost = 500

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': '100 Virtual Shelter Tokens',
                    },
                    'unit_amount': token_cost,
                },
                'quantity': 1,
                }
            ],
            mode='payment',
            # success_url=YOUR_DOMAIN + '/success.html',
            # cancel_url=YOUR_DOMAIN + '/cancel.html',
            success_url='http://127.0.0.1:8000/profiles/tokens/success/',
            cancel_url='http://127.0.0.1:8000/profiles/tokens/cancel/',
            metadata={
                'user_id': request.user.id
            }
        )
        return redirect(checkout_session.url, code=302)
    except Exception as e:
        print("Stripe session creation error:", e)
        return JsonResponse({'error': str(e)}, status=500)
    

@login_required
def success_view(request):
    return HttpResponse("Payment successful! Tokens have been added to your account.")


@login_required
def cancel_view(request):
    return HttpResponse("Payment canceled. No tokens were added.")

    
@csrf_exempt
def stripe_webhook(request):
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
                profile.tokens += 10
                profile.save()
            except Profile.DoesNotExist:
                return JsonResponse({'status': 'User profile not found'}, status=404)

    return JsonResponse({'status': 'success'}, status=200)