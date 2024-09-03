from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from shelters.models import Shelter
from .models import Animal
from animals.forms import AnimalForm


# Views
class AddAnimalViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(admin=self.user, name="Test Shelter", registration_number="123456789", description="A test shelter")
        self.client.login(username='testuser', password='12345')
    
    def test_redirect_if_no_shelter(self):
        self.shelter.delete()
        response = self.client.get('/animals/add/')
        self.assertRedirects(response, '/shelters/my-shelter/')
    
    def test_add_animal_post_request(self):
        data = {
            'name': 'Test Animal',
            'species': 'Dog',
            'age': 4,
            'adoption_status': 'available',
        }
        response = self.client.post('/animals/add/', data)

        self.assertRedirects(response, '/shelters/my-shelter/')
        self.assertEqual(Animal.objects.count(), 1)
        self.assertEqual(Animal.objects.first().shelter, self.shelter)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(admin=self.user, name="Test Shelter", registration_number="123456789", description="A test shelter")
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            age=4,
            adoption_status='available'
        )

    def test_profile_view_with_valid_id(self):
        url = f'/animals/profile/{self.animal.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/profile.html')
        self.assertContains(response, self.animal.name)

    def test_profile_view_with_invalid_id(self):
        url = f'/animals/profile/999/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')


class EditProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(admin=self.user, name="Test Shelter", registration_number="123456789", description="A test shelter")
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            age=4,
            description="A friendly dog",
            adoption_status='available'
        )
        self.client.login(username='testuser', password='12345')

    def test_edit_profile_view_unauthorized_user(self):
        # Test that a user who is not the admin cannot edit the profile
        other_user = User.objects.create_user(username='otheruser', password='12345')
        self.client.login(username='otheruser', password='12345')
        
        response = self.client.get(f'/animals/edit-profile/{self.animal.id}/')
        
        self.assertRedirects(response, '/')
    
    def test_edit_profile_view_get(self):
        # Test that the edit profile page renders correctly
        url = f'/animals/edit-profile/{self.animal.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/edit_profile.html')
        self.assertIsInstance(response.context['form'], AnimalForm)
        self.assertEqual(response.context['form'].instance, self.animal)
    
    def test_edit_profile_view_post_valid(self):
        # Test POST request with valid data
        data = {
            'name': 'Updated Animal Name',
            'species': 'Cat',
            'age': 5,
            'description': 'A friendly cat',
            'adoption_status': 'fostered'
        }
        response = self.client.post(f'/animals/edit-profile/{self.animal.id}/', data)
        
        self.animal.refresh_from_db()
        self.assertRedirects(response, f'/animals/profile/{self.animal.id}/')
        self.assertEqual(self.animal.name, 'Updated Animal Name')
        self.assertEqual(self.animal.species, 'Cat')
        self.assertEqual(self.animal.age, 5)
        self.assertEqual(self.animal.description, 'A friendly cat')
        self.assertEqual(self.animal.adoption_status, 'fostered')
    
    def test_edit_profile_view_with_invalid_data(self):
        # Test POST request with invalid data
        data = {
            'name': '', # Name is required
            'species': 'Dog',
            'age': 4,
        }
        response = self.client.post(f'/animals/edit-profile/{self.animal.id}/', data)
        
        # Should rerender page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/edit_profile.html')
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('name', response.context['form'].errors)

class DeleteProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(admin=self.user, name="Test Shelter", registration_number="123456789", description="A test shelter")
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            age=4,
            description="A friendly dog",
            adoption_status='available'
        )
    
    def test_delete_animal_profile_as_admin(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(f'/animals/delete-profile/{self.animal.id}/')
        self.assertRedirects(response, '/')
        self.assertFalse(Animal.objects.filter(id=self.animal.id).exists())

    def test_delete_animal_profile_as_non_admin(self):
        other_user = User.objects.create_user(username='otheruser', password='12345')
        self.client.login(username='otheruser', password='12345')
        response = self.client.post(f'/animals/delete-profile/{self.animal.id}/')
        self.assertRedirects(response, '/profiles/')
        self.assertTrue(Animal.objects.filter(id=self.animal.id).exists())

    def test_delete_animal_profile_invalid_id(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post('/animals/delete-profile/999/')
        self.assertEqual(response.status_code, 404)


class ViewAnimalsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name="Test Shelter1",
            registration_number="12345",
            website="http://example.com",
            description="A test shelter1."
        )
        self.animal = Animal.objects.create(
            shelter = self.shelter,
            name = "Sky",
            species = "Dog",
            breed = "Collie",
            age = 3,
            description = "A honey bunny",
            adoption_status = "available"
        )
    
    def test_view(self):
        response = self.client.get('/animals/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/view_animals.html')
        self.assertIn('animals', response.context)
        self.assertEqual(len(response.context['animals']), 1)


# Models
class AnimalModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(admin=self.user, name="Test Shelter", registration_number="123456789", description="A test shelter")
    
    def test_animal_creation(self):
        animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            breed="Labrador",
            age=3,
            description="A friendly dog",
            adoption_status="available"
        )
        self.assertEqual(animal.name, "Test Animal")
        self.assertEqual(animal.species, "Dog")
        self.assertEqual(animal.breed, "Labrador")
        self.assertEqual(animal.age, 3)
        self.assertEqual(animal.description, "A friendly dog")
        self.assertEqual(animal.adoption_status, "available")
        self.assertEqual(animal.shelter, self.shelter)

    def test_string_representation(self):
        animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            age=3
        )
        expected_string = f"{animal.name} - {self.shelter}"
        self.assertEqual(str(animal), expected_string)
    
    def test_animal_without_optional_fields(self):
        # Animal instance without optional fields
        animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Cat",
            age=2
        )
        self.assertIsNone(animal.breed)
        self.assertIsNone(animal.description)
        self.assertEqual(animal.adoption_status, "available")  # Default status

    def test_animal_missing_required_fields(self):
        with self.assertRaises(IntegrityError):
            Animal.objects.create(shelter=self.shelter)

