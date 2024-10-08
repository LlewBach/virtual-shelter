from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.admin.sites import site
from django.utils import timezone
from django.core import mail
from django.conf import settings
from unittest.mock import patch, Mock
import stripe
import json
from shelters.models import Shelter
from animals.models import Animal
from .models import Profile, RoleChangeRequest
from .admin import ProfileAdmin, RoleChangeRequestAdmin
from .forms import ProfileForm, RoleChangeRequestForm


# Views
class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(admin=self.user, name="Test Shelter", registration_number="123456789", description="A test shelter")
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name='Buddy',
            species='Dog',
            age=3,
            description='Good doggo',
            adoption_status='Available',
            fosterer=self.user.profile
        )

    def test_profile_view(self):
        response = self.client.get('/profiles/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile.html')
        self.assertContains(response, 'Role: user')
        self.assertIn(self.animal, response.context['animals'])

    def test_profile_requires_login(self):
        response = self.client.get('/profiles/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.get('/profiles/')
        self.assertNotEqual(response.status_code, 200)


class EditProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_edit_profile_get(self):
        """
        Test accessing the edit profile page with a GET request.
        """
        response = self.client.get('/profiles/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/edit_profile.html')
        self.assertIsInstance(response.context['form'], ProfileForm)

    def test_edit_profile_post_valid(self):
        """
        Test submitting valid data with a POST request to update the profile.
        """
        url = '/profiles/edit/'
        data = {
            'bio': 'Hello there!',
        }
        response = self.client.post(url, data)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, 'Hello there!')
        self.assertRedirects(response, '/profiles/')


class DeleteProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.user.profile.bio = 'Test bio'

    def test_delete_profile_post_request(self):
        response = self.client.post('/profiles/delete/')
        self.assertRedirects(response, '/')
        self.assertFalse(User.objects.filter(username='testuser').exists())
        self.assertFalse(Profile.objects.filter(bio='Test bio').exists())

    def test_delete_profile_get_request(self):
        response = self.client.get('/profiles/delete/')
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTemplateUsed(response, 'profiles/profile.html')
        self.assertEqual(response.status_code, 200)


class ApplyForRoleChangeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_apply_for_role_change_requires_login(self):
        response = self.client.get('/profiles/apply-role-change/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.get('/profiles/apply-role-change/')
        self.assertNotEqual(response.status_code, 200)        

    def test_apply_for_role_change_valid_submission(self):
        form_data = {
            'charity_name': 'Test Charity',
            'charity_registration_number': '123456',
            'charity_website': 'https://testcharity.com',
            'charity_description': 'A charity description.',
        }
        response = self.client.post('/profiles/apply-role-change/', form_data)
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, '/shelters/my-shelter/')
        self.assertTrue(RoleChangeRequest.objects.filter(user=self.user).exists())

    def test_apply_for_role_change_invalid_submission(self):
        # Simulate an invalid form submission (e.g., missing required fields)
        form_data = {
            'charity_name': '',
            'charity_registration_number': '',
            'charity_website': '',
            'charity_description': '',
        }
        response = self.client.post('/profiles/apply-role-change/', form_data)
        # Should re-render the form with errors
        self.assertEqual(response.status_code, 200)
        # Check that no request was created
        self.assertFalse(RoleChangeRequest.objects.filter(user=self.user).exists())  


class TokensViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_tokens_view(self):
        response = self.client.get('/profiles/tokens/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/tokens.html')
        self.assertEqual(response.context['profile'], self.user.profile)


class CheckoutSessionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
    
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_stripe_create):
        # Mock the Stripe checkout session response

        mock_stripe_create.return_value = Mock(
            id='cs_test_session_id',
            url='https://mock-checkout-url'
        )

        response = self.client.post('/profiles/create-checkout-session/')

        # Check correct parameters for Stripe
        mock_stripe_create.assert_called_with(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': '100 Virtual Shelter Tokens'},
                        'unit_amount': 500,
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url='http://testserver/profiles/tokens/success/',
            cancel_url='http://testserver/profiles/tokens/cancel/',
            metadata={'user_id': self.user.id},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://mock-checkout-url')


class SuccessAndCancelViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
    
    def test_success_view_authenticated(self):
        response = self.client.get('/profiles/tokens/success/')

        self.assertEqual(response.status_code, 200)

    def test_cancel_view_authenticated(self):
        response = self.client.get('/profiles/tokens/cancel/')

        self.assertEqual(response.status_code, 200)


class StripeWebhookTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    @patch('stripe.Webhook.construct_event')
    def test_valid_webhook_event(self, mock_construct_event):
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'metadata': {
                        'user_id': str(self.user.id),
                    }
                }
            }
        }

        mock_construct_event.return_value = mock_event

        response = self.client.post(
            '/profiles/stripe-webhook/',
            data=json.dumps({'dummy': 'data'}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='dummy_signature'
        )

        self.assertEqual(response.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.tokens, 100)

    @patch('stripe.Webhook.construct_event')
    def test_invalid_signature(self, mock_construct_event):
        # Simulate SignatureVerificationError
        mock_construct_event.side_effect = stripe.error.SignatureVerificationError('Invalid signature', 'some_header')

        response = self.client.post(
            '/profiles/stripe-webhook/',
            data=json.dumps({'dummy': 'data'}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='dummy_signature'
        )

        # Assert 400 error for invalid signature
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'status': 'Invalid signature'})


# Models
class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_profile_creation(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
    
    def test_profile_str(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(str(profile), 'testuser Profile')


class RoleChangeRequestModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.role_change_request = RoleChangeRequest.objects.create(
            user=self.user,
            charity_name='Test Charity',
            charity_registration_number='123456',
            charity_website='https://testcharity.org',
            charity_description='A test charity.',
            status='pending'
        )

    def test_role_change_request_creation(self):
        self.assertEqual(self.role_change_request.user, self.user)
        self.assertEqual(self.role_change_request.charity_name, 'Test Charity')
        self.assertEqual(self.role_change_request.charity_registration_number, '123456')
        self.assertEqual(self.role_change_request.charity_website, 'https://testcharity.org')
        self.assertEqual(self.role_change_request.charity_description, 'A test charity.')
        self.assertEqual(self.role_change_request.status, 'pending')

    def test_str(self):
        expected_str = f'{self.user.username} - Test Charity - pending'
        self.assertEqual(str(self.role_change_request), expected_str)


# Admins
class ProfileAdminTest(TestCase):
    def test_profile_admin_registration(self):
        self.assertIn(Profile, site._registry)

    def test_profile_admin_list_display(self):
        profile_admin = ProfileAdmin(Profile, site)
        self.assertEqual(profile_admin.list_display, ('user', 'role'))


class RoleChangeRequestAdminTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = Profile.objects.get(user=self.user)
        self.role_change_request = RoleChangeRequest.objects.create(
            user=self.user,
            charity_name='Test Charity',
            charity_registration_number='123456',
            charity_website='https://testcharity.org',
            charity_description='A test charity.',
            status='pending'
        )

    def test_role_change_request_admin_registration(self):
        self.assertIn(RoleChangeRequest, site._registry)

    def test_role_change_request_admin_list_display(self):
        # Test if the list_display in RoleChangeRequestAdmin is correctly set
        role_change_request_admin = RoleChangeRequestAdmin(RoleChangeRequest, site)
        self.assertEqual(role_change_request_admin.list_display, 
                         ('user', 'charity_name', 'charity_registration_number', 
                          'charity_website', 'charity_description', 'status'))

    def test_approve_requests_action(self):
        # Simulate approving the request
        role_change_request_admin = RoleChangeRequestAdmin(RoleChangeRequest, site)
        queryset = RoleChangeRequest.objects.filter(id=self.role_change_request.id)
        role_change_request_admin.approve_requests(None, queryset)

        # Refresh from the database
        self.role_change_request.refresh_from_db()
        self.profile.refresh_from_db()

        # Test if the request was approved
        self.assertEqual(self.role_change_request.status, 'approved')
        self.assertEqual(self.profile.role, 'shelter_admin')

    def test_reject_requests_action(self):
        # Simulate rejecting the request
        role_change_request_admin = RoleChangeRequestAdmin(RoleChangeRequest, site)
        queryset = RoleChangeRequest.objects.filter(id=self.role_change_request.id)
        role_change_request_admin.reject_requests(None, queryset)

        # Refresh from the database
        self.role_change_request.refresh_from_db()

        # Test if the request was rejected
        self.assertEqual(self.role_change_request.status, 'rejected')
        # Test profile role unchanged
        self.assertEqual(self.profile.role, 'user')


# Forms
class RoleChangeRequestFormTest(TestCase):
    def test_form_initialization(self):
        """Test if the form initializes without any errors"""
        form = RoleChangeRequestForm()
        self.assertIsNotNone(form)

    def test_form_valid_data(self):
        """Test the form with valid data"""
        form_data = {
            'charity_name': 'Test Charity',
            'charity_registration_number': '123456',
            'charity_website': 'https://testcharity.org',
            'charity_description': 'A test charity.',
        }
        form = RoleChangeRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        """Test the form with missing required fields"""
        form_data = {
            'charity_name': '',
            'charity_registration_number': '',
            'charity_website': 'invalid-url',  # Invalid URL
            'charity_description': '',
        }
        form = RoleChangeRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('charity_name', form.errors)
        self.assertIn('charity_registration_number', form.errors)
        self.assertIn('charity_website', form.errors)

    def test_charity_description_widget(self):
        """Test the widget configuration for charity_description field"""
        form = RoleChangeRequestForm()
        self.assertEqual(form.fields['charity_description'].widget.attrs['rows'], 4)


# Signals
class RoleChangeRequestSignalTest(TestCase):
    def setUp(self):
        # Create a superuser
        self.superuser = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        # Create a regular user
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password'
        )

    def test_notify_superuser_on_role_change_request(self):
        # Before creating request, check no emails sent
        self.assertEqual(len(mail.outbox), 0)
        
        # Create a role change request
        RoleChangeRequest.objects.create(
            user=self.user,
            charity_name='Test Charity',
            charity_registration_number='123456',
            charity_website='http://testcharity.org',
            charity_description='A test charity'
        )
        
        # Check that an email has been sent
        self.assertEqual(len(mail.outbox), 1)

        # Verify the contents of the email
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'New Shelter Admin Role Change Request')
        self.assertIn('A new role change request has been submitted by testuser.', email.body)
        self.assertIn('Test Charity', email.body)
        self.assertIn('123456', email.body)
        self.assertIn('http://testcharity.org', email.body)
        self.assertIn('A test charity', email.body)
        self.assertEqual(email.to, [self.superuser.email])
