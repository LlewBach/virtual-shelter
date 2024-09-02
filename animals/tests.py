from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from shelters.models import Shelter
from .models import Animal
from .forms import AnimalForm


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

