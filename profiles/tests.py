from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.admin.sites import site
from django.utils import timezone
from django.core import mail
from django.conf import settings
from .models import Profile, RoleChangeRequest
from .admin import ProfileAdmin, RoleChangeRequestAdmin
from .forms import RoleChangeRequestForm


# Views
class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_profile_view(self):
        response = self.client.get('/profiles/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile.html')
        self.assertContains(response, 'Role: user')

    def test_profile_requires_login(self):
        response = self.client.get('/profiles/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.get('/profiles/')
        self.assertNotEqual(response.status_code, 200)        


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
