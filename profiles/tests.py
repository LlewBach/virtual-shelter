from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.admin.sites import site
from django.contrib.messages import get_messages
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
    """
    Test cases for the profile view.
    
    Ensures that the profile page is rendered correctly and requires login.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user, logging in, 
        and creating a shelter and an animal associated with the user's profile.
        """
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
        """
        Test that the profile page loads correctly with the user's profile and associated animals.
        """
        response = self.client.get('/profiles/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile.html')
        self.assertEqual(self.user.profile, response.context['profile'])
        self.assertIn(self.animal, response.context['animals'])

    def test_profile_requires_login(self):
        """
        Test that the profile page requires a logged-in user to access.
        """
        response = self.client.get('/profiles/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.get('/profiles/')
        self.assertNotEqual(response.status_code, 200)


class EditProfileViewTest(TestCase):
    """
    Test cases for the edit profile view.
    
    Ensures correct behavior when accessing or submitting data to the edit profile page.
    """
    def setUp(self):
        """
        Set up the test environment by creating and logging in a user.
        """
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

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Profile saved")

    def test_profile_not_found(self):
        """
        Test behavior when profile is not found.
        """
        self.user.profile.delete()
        response = self.client.get('/profiles/edit/')
        self.assertRedirects(response, '/')
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Profile not found")


class DeleteProfileViewTest(TestCase):
    """
    Test cases for the delete profile view.
    
    Ensures correct behavior when a user requests to delete their profile.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user and logging them in.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.user.profile.bio = 'Test bio'

    def test_delete_profile_post_request(self):
        """
        Test deleting the profile with a POST request.
        """
        response = self.client.post('/profiles/delete/')
        self.assertRedirects(response, '/')
        self.assertFalse(User.objects.filter(username='testuser').exists())
        self.assertFalse(Profile.objects.filter(bio='Test bio').exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Profile deleted")
    
    def test_delete_profile_post_request_error(self):
        """
        Test error handling during profile deletion.
        """
        # Simulate an error in deletion by mocking the delete method
        with patch('django.contrib.auth.models.User.delete', side_effect=Exception('Deletion error')):
            response = self.client.post('/profiles/delete/')
            self.assertRedirects(response, '/profiles/')
            
            # Check if error message was added
            messages = list(get_messages(response.wsgi_request))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), "Error deleting profile")


    def test_delete_profile_get_request(self):
        """
        Test accessing the delete profile page with a GET request.
        """
        response = self.client.get('/profiles/delete/')
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTemplateUsed(response, 'profiles/profile.html')
        self.assertEqual(response.status_code, 200)


class ApplyForRoleChangeViewTest(TestCase):
    """
    Test cases for the apply for role change view.
    
    Ensures the correct behavior when accessing and submitting the role change request form.
    """
    def setUp(self):
        """
        Set up the test environment by creating and logging in a user.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_apply_for_role_change_requires_login(self):
        """
        Test that the apply for role change page requires a logged-in user.
        """
        response = self.client.get('/profiles/apply-role-change/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.get('/profiles/apply-role-change/')
        self.assertNotEqual(response.status_code, 200)        

    def test_apply_for_role_change_valid_submission(self):
        """
        Test submitting a valid role change request form.
        """
        form_data = {
            'charity_name': 'Test Charity',
            'charity_registration_number': '123456',
            'charity_website': 'https://testcharity.com',
            'charity_description': 'A charity description.',
        }
        response = self.client.post('/profiles/apply-role-change/', form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/dashboard/')
   
        self.assertTrue(RoleChangeRequest.objects.filter(user=self.user).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Request submitted")

    def test_apply_for_role_change_invalid_submission(self):
        """
        Test submitting an invalid role change request form.
        """
        form_data = {
            'charity_name': '',
            'charity_registration_number': '',
            'charity_website': '',
            'charity_description': '',
        }
        response = self.client.post('/profiles/apply-role-change/', form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(RoleChangeRequest.objects.filter(user=self.user).exists())  

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Error with request")


class TokensViewTest(TestCase):
    """
    Test cases for the tokens view.
    
    Ensures correct behavior when accessing the tokens page.
    """
    def setUp(self):
        """
        Set up the test environment by creating and logging in a user.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_tokens_view(self):
        """
        Test accessing the tokens view with a GET request.
        """
        response = self.client.get('/profiles/tokens/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/tokens.html')
        self.assertEqual(response.context['profile'], self.user.profile)


class CheckoutSessionTest(TestCase):
    """
    Test case for creating a Stripe checkout session.
    
    Ensures that the checkout session is correctly created and the user is 
    redirected to the Stripe checkout page.
    """
    def setUp(self):
        """
        Set up the test environment by creating and logging in a user.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
    
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_stripe_create):
        """
        Test creating a Stripe checkout session and ensure the user is 
        redirected to the mock Stripe checkout URL.
        """
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
                        'currency': 'gbp',
                        'product_data': {'name': '100 Virtual Shelter Tokens'},
                        'unit_amount': 499,
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url='http://testserver/dashboard/?payment_status=success',
            cancel_url='http://testserver/dashboard/?payment_status=cancel',
            metadata={'user_id': self.user.id},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://mock-checkout-url')


class StripeWebhookTest(TestCase):
    """
    Test cases for handling Stripe webhook events.
    
    Ensures that the webhook endpoint correctly processes valid events 
    and handles errors such as invalid signatures.
    """
    def setUp(self):
        """
        Set up the test environment by creating and logging in a user.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    @patch('stripe.Webhook.construct_event')
    def test_valid_webhook_event(self, mock_construct_event):
        """
        Test processing a valid Stripe webhook event (checkout.session.completed).
        """
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
        """
        Test handling of an invalid Stripe webhook signature.
        """
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
    """
    Test cases for the Profile model.
    
    Ensures that the Profile is created correctly and the __str__ method functions as expected.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_profile_creation(self):
        """
        Test that a Profile is automatically created when a User is created.
        """
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
    
    def test_profile_str(self):
        """
        Test the __str__ method of the Profile model.
        """
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(str(profile), 'testuser Profile')


class RoleChangeRequestModelTest(TestCase):
    """
    Test cases for the RoleChangeRequest model.
    
    Ensures that RoleChangeRequest objects are created correctly and the 
    __str__ method returns the expected string.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user and a RoleChangeRequest.
        """
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
        """
        Test that a RoleChangeRequest object is created with the correct data.
        """
        self.assertEqual(self.role_change_request.user, self.user)
        self.assertEqual(self.role_change_request.charity_name, 'Test Charity')
        self.assertEqual(self.role_change_request.charity_registration_number, '123456')
        self.assertEqual(self.role_change_request.charity_website, 'https://testcharity.org')
        self.assertEqual(self.role_change_request.charity_description, 'A test charity.')
        self.assertEqual(self.role_change_request.status, 'pending')

    def test_str(self):
        """
        Test the __str__ method of the RoleChangeRequest model.
        """
        expected_str = f'{self.user.username} - Test Charity - pending'
        self.assertEqual(str(self.role_change_request), expected_str)


# Admins
class ProfileAdminTest(TestCase):
    """
    Test cases for the Profile model's admin configuration.
    
    Ensures that the Profile model is correctly registered in the admin site 
    and that the list display is properly configured.
    """
    def test_profile_admin_registration(self):
        """
        Test that the Profile model is registered with the admin site.
        """
        self.assertIn(Profile, site._registry)

    def test_profile_admin_list_display(self):
        """
        Test that the list display in the ProfileAdmin includes 'user' and 'role'.
        """
        profile_admin = ProfileAdmin(Profile, site)
        self.assertEqual(profile_admin.list_display, ('user', 'role'))


class RoleChangeRequestAdminTest(TestCase):
    """
    Test cases for the RoleChangeRequest model's admin configuration.
    
    Ensures that the RoleChangeRequest model is registered in the admin site, 
    checks list display settings, and tests custom admin actions for approving 
    and rejecting requests.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user, profile, and role change request.
        """
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
        """
        Test that the RoleChangeRequest model is registered with the admin site.
        """
        self.assertIn(RoleChangeRequest, site._registry)

    def test_role_change_request_admin_list_display(self):
        """
        Test that the list display in RoleChangeRequestAdmin includes the correct fields.
        """
        role_change_request_admin = RoleChangeRequestAdmin(RoleChangeRequest, site)
        self.assertEqual(role_change_request_admin.list_display, 
                         ('user', 'charity_name', 'charity_registration_number', 
                          'charity_website', 'charity_description', 'status'))

    def test_approve_requests_action(self):
        """
        Test the custom admin action for approving role change requests.
        """
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
        """
        Test the custom admin action for rejecting role change requests.
        """
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
    """
    Test cases for the RoleChangeRequestForm.
    
    Ensures proper initialization, validation, and widget configuration of the form.
    """
    def test_form_initialization(self):
        """
        Test if the form initializes without any errors.
        """
        form = RoleChangeRequestForm()
        self.assertIsNotNone(form)

    def test_form_valid_data(self):
        """
        Test the form with valid data.
        """
        form_data = {
            'charity_name': 'Test Charity',
            'charity_registration_number': '123456',
            'charity_website': 'https://testcharity.org',
            'charity_description': 'A test charity.',
        }
        form = RoleChangeRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        """
        Test the form with missing required fields.
        """
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
        """
        Test the widget configuration for charity_description field
        """
        form = RoleChangeRequestForm()
        self.assertEqual(form.fields['charity_description'].widget.attrs['rows'], 4)


# Signals
class RoleChangeRequestSignalTest(TestCase):
    """
    Test cases for the signal that notifies superusers when a role change request is created.
    
    Ensures that an email notification is sent to superusers when a RoleChangeRequest is created.
    """
    def setUp(self):
        """
        Set up the test environment by creating a superuser and a regular user.
        """
        self.superuser = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password'
        )

    def test_notify_superuser_on_role_change_request(self):
        """
        Test that an email is sent to superusers when a role change request is created.
        """
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
