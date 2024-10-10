from django.test import TestCase
from django.contrib.messages import get_messages
from django.contrib.auth.models import User
from profiles.models import RoleChangeRequest
from .models import Shelter
from animals.models import Animal
from .forms import ShelterForm


# Views
class ShelterViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name='Test Shelter',
            registration_number='123456',
            website='http://www.testshelter.com',
            description='This is a test shelter.'
        )
        self.client.login(username='testuser', password='testpassword')

    def test_shelter_view_with_shelter(self):
        response = self.client.get(f'/shelters/profile/{self.shelter.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shelters/shelter.html')
        self.assertIn('shelter', response.context)
        self.assertEqual(response.context['shelter'], self.shelter)

    def test_shelter_view_with_animals(self):        
        Animal.objects.create(shelter=self.shelter, name="Test Animal 1", species="Dog", age=5, adoption_status="Available")
        Animal.objects.create(shelter=self.shelter, name="Test Animal 2", species="Cat", age=1, adoption_status="Fostered")
        
        response = self.client.get(f'/shelters/profile/{self.shelter.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Animal 1")
        self.assertContains(response, "Test Animal 2")

    def test_shelter_view_shelter_does_not_exist(self):
        non_existent_id = 999
        response = self.client.get(f'/shelters/profile/{non_existent_id}/')

        self.assertRedirects(response, '/shelters/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The shelter you are looking for does not exist.")


class EditMyShelterViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name='Test Shelter',
            registration_number='123456789',
            website='https://www.testshelter.com',
            description='A test shelter description.'
        )
        self.client.login(username='testuser', password='testpass')

    def test_edit_shelter_view_get(self):
        # Test GET request to the edit_my_shelter view
        response = self.client.get(f'/shelters/profile/edit/{self.shelter.id}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shelters/edit_shelter.html')
        self.assertIsInstance(response.context['form'], ShelterForm)
        self.assertEqual(response.context['form'].instance, self.shelter)

    def test_edit_shelter_view_post_valid(self):
        # Test POST request with valid data
        data = {
            'name': 'Updated Test Shelter',
            'registration_number': '987654321',
            'website': 'https://www.updatedshelter.com',
            'description': 'An updated description.'
        }
        response = self.client.post(f'/shelters/profile/edit/{self.shelter.id}/', data)

        self.shelter.refresh_from_db()
        self.assertRedirects(response, f'/shelters/profile/{self.shelter.id}/')
        self.assertEqual(self.shelter.name, 'Updated Test Shelter')
        self.assertEqual(self.shelter.registration_number, '987654321')
        self.assertEqual(self.shelter.website, 'https://www.updatedshelter.com')
        self.assertEqual(self.shelter.description, 'An updated description.')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"'{self.shelter.name}' updated")

    def test_edit_shelter_view_post_invalid(self):
        # Test POST request with invalid data
        data = {
            'name': '',  # Name is required
            'registration_number': '987654321',
            'website': 'https://www.updatedshelter.com',
            'description': 'An updated description.'
        }
        response = self.client.post(f'/shelters/profile/edit/{self.shelter.id}/', data)

        # Should rerender page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shelters/edit_shelter.html')
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('name', response.context['form'].errors)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Error updating shelter - Check the form")

    def test_edit_shelter_view_no_shelter(self):
        # Test when the user has no shelter
        id = self.shelter.id
        self.shelter.delete()
        response = self.client.get(f'/shelters/profile/edit/{id}/')
        self.assertRedirects(response, '/shelters/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Shelter not found")

class DeleteMyShelterViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name="Test Shelter",
            registration_number="12345",
            website="http://example.com",
            description="A test shelter."
        )

    def test_delete_shelter_post_request(self):
        response = self.client.post('/shelters/profile/delete/')
        self.assertRedirects(response, '/')
        self.assertFalse(User.objects.filter(username='testuser').exists())
        self.assertFalse(Shelter.objects.filter(name='Test Shelter').exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Account deleted")

    def test_delete_shelter_error(self):
        """
        Test what happens when there's an error deleting the user or shelter.
        """
        # Simulate an error by overriding the delete method temporarily
        original_delete = User.delete
        User.delete = lambda self: (_ for _ in ()).throw(Exception("Deletion error"))

        response = self.client.post('/shelters/profile/delete/')

        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(Shelter.objects.filter(name='Test Shelter').exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Error deleting account")

        # Revert the User.delete method to its original state
        User.delete = original_delete


class ViewSheltersViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name="Test Shelter1",
            registration_number="12345",
            website="http://example.com",
            description="A test shelter1."
        )

    def test_view(self):
        response = self.client.get('/shelters/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shelters/view_shelters.html')
        self.assertIn('shelters', response.context)
        self.assertEqual(len(response.context['shelters']), 1)


# Models
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


# Signals
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