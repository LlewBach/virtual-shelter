from django.test import TestCase
from django.contrib.auth.models import User
from profiles.models import RoleChangeRequest
from .models import Shelter

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Shelter

class MyShelterViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # Create a shelter associated with the test user
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name='Test Shelter',
            registration_number='123456',
            website='http://www.testshelter.com',
            description='This is a test shelter.'
        )

    def test_my_shelter_view_with_shelter(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/shelters/my-shelter/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shelters/my_shelter.html')

        # Check that the shelter is in the context
        self.assertIn('my_shelter', response.context)
        self.assertEqual(response.context['my_shelter'], self.shelter)


class ShelterModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name='Test Shelter',
            registration_number='12345',
            website='https://testshelter.com',
            description='This is a test shelter description.'
        )

    def test_shelter_creation(self):
        # Test that the shelter was created correctly
        self.assertEqual(self.shelter.name, 'Test Shelter')
        self.assertEqual(self.shelter.registration_number, '12345')
        self.assertEqual(self.shelter.website, 'https://testshelter.com')
        self.assertEqual(self.shelter.description, 'This is a test shelter description.')
        self.assertEqual(self.shelter.admin, self.user)

    def test_str(self):
        self.assertEqual(str(self.shelter), 'Test Shelter')

    def test_shelter_admin_relationship(self):
        # Test the relationship between Shelter and User
        self.assertEqual(self.shelter.admin.username, 'testuser')

# Signal test
class CreateShelterOnApprovalTest(TestCase):
    def setUp(self):
        # Create a user instance
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_shelter_creation_on_role_approval(self):
        # Create a RoleChangeRequest with 'approved' status
        role_change_request = RoleChangeRequest.objects.create(
            user=self.user,
            charity_name='Test Charity',
            charity_registration_number='12345',
            charity_website='https://testcharity.com',
            charity_description='A test charity description.',
            status='approved'
        )

        # Fetch the shelter created by the signal
        shelter = Shelter.objects.get(admin=self.user)

        # Check that the Shelter was created with the correct details
        self.assertEqual(shelter.name, 'Test Charity')
        self.assertEqual(shelter.registration_number, '12345')
        self.assertEqual(shelter.website, 'https://testcharity.com')
        self.assertEqual(shelter.description, 'A test charity description.')

    def test_no_shelter_created_on_non_approved_status(self):
        # Create a RoleChangeRequest with a status other than 'approved'
        role_change_request = RoleChangeRequest.objects.create(
            user=self.user,
            charity_name='Test Charity',
            charity_registration_number='12345',
            charity_website='https://testcharity.com',
            charity_description='A test charity description.',
            status='rejected'
        )

        # Check that no Shelter was created
        with self.assertRaises(Shelter.DoesNotExist):
            Shelter.objects.get(admin=self.user)

    def test_no_duplicate_shelter_created(self):
        # Create a Shelter for the user first
        existing_shelter = Shelter.objects.create(
            admin=self.user,
            name='Existing Shelter',
            registration_number='54321',
            website='https://existingshelter.com',
            description='An existing shelter description.'
        )

        # Create a RoleChangeRequest with 'approved' status
        role_change_request = RoleChangeRequest.objects.create(
            user=self.user,
            charity_name='Test Charity',
            charity_registration_number='12345',
            charity_website='https://testcharity.com',
            charity_description='A test charity description.',
            status='approved'
        )

        # There should still be only one shelter for this user
        shelters = Shelter.objects.filter(admin=self.user)
        self.assertEqual(shelters.count(), 1)
        self.assertEqual(shelters.first(), existing_shelter)