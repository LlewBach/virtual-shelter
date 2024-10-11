import os
from django.conf import settings
from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from django.contrib.auth.models import User
from shelters.models import Shelter
from .models import Animal, Update
from animals.forms import AnimalForm, UpdateForm
from datetime import datetime


# Views
class AddAnimalViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(admin=self.user, name="Test Shelter", registration_number="123456789", description="A test shelter")
        self.client.login(username='testuser', password='12345')
    
    def test_redirect_if_no_shelter(self):
        self.shelter.delete()
        response = self.client.get('/animals/add/')
        self.assertRedirects(response, '/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You aren't a shelter admin")
        self.assertEqual(messages[0].tags, 'error')
    
    def test_add_animal_post_request(self):
        data = {
            'name': 'Test Animal',
            'species': 'Dog',
            'age': 4,
            'adoption_status': 'Available',
        }
        response = self.client.post('/animals/add/', data)

        self.assertRedirects(response, f'/shelters/profile/{self.shelter.id}/')
        self.assertEqual(Animal.objects.count(), 1)
        self.assertEqual(Animal.objects.first().shelter, self.shelter)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Animal 'Test Animal' added")
        self.assertEqual(messages[0].tags, 'success')

    def test_invalid_add_animal_post_request(self):
        """
        Test an invalid POST request (e.g., missing required fields) to ensure the form is re-rendered with errors.
        """
        data = {
            'name': '',
            'species': 'Dog',
            'age': 4,
            'adoption_status': 'Available',
        }
        response = self.client.post('/animals/add/', data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Animal.objects.count(), 0)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Error adding animal. Check form")
        self.assertEqual(messages[0].tags, 'error')


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(admin=self.user, name="Test Shelter", registration_number="123456789", description="A test shelter")
        self.image = SimpleUploadedFile(name='test_image.jpg', content=b"dummy image data", content_type='image/jpeg')
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            age=4,
            adoption_status='Available',
            image=self.image
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

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Animal not found")
        self.assertEqual(messages[0].level_tag, 'error')

    def tearDown(self):
        # Delete the file after test
        if self.animal.image:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.animal.image.name))

        super().tearDown()


class EditProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(admin=self.user, name="Test Shelter", registration_number="123456789", description="A test shelter")
        self.image = SimpleUploadedFile(name='test_image.jpg', content=b"dummy image data", content_type='image/jpeg')
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            age=4,
            description="A friendly dog",
            adoption_status='Available',
            image=self.image
        )
        self.client.login(username='testuser', password='12345')

    def test_edit_profile_view_unauthorized_user(self):
        # Test that a user who is not the admin cannot edit the profile
        other_user = User.objects.create_user(username='otheruser', password='12345')
        self.client.login(username='otheruser', password='12345')
        
        response = self.client.get(f'/animals/edit-profile/{self.animal.id}/')
        self.assertRedirects(response, '/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Only shelter admin can edit animal")
    
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
            'species': 'Dog',
            'age': 5,
            'description': 'A friendly dog',
            'adoption_status': 'Fostered'
        }
        response = self.client.post(f'/animals/edit-profile/{self.animal.id}/', data)
        
        self.animal.refresh_from_db()
        self.assertRedirects(response, f'/animals/profile/{self.animal.id}/')
        self.assertEqual(self.animal.name, 'Updated Animal Name')
        self.assertEqual(self.animal.species, 'Dog')
        self.assertEqual(self.animal.age, 5)
        self.assertEqual(self.animal.description, 'A friendly dog')
        self.assertEqual(self.animal.adoption_status, 'Fostered')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Animal saved")
    
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

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Error saving animal - Check the form")
    
    def tearDown(self):
        # Delete the file after test
        if self.animal.image:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.animal.image.name))

        super().tearDown()

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
            adoption_status='Available'
        )
    
    def test_delete_animal_profile_as_admin(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(f'/animals/delete-profile/{self.animal.id}/')
        self.assertRedirects(response, '/')
        self.assertFalse(Animal.objects.filter(id=self.animal.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), f"Animal '{self.animal.name}' deleted.")

    def test_delete_animal_profile_as_non_admin(self):
        other_user = User.objects.create_user(username='otheruser', password='12345')
        self.client.login(username='otheruser', password='12345')
        response = self.client.post(f'/animals/delete-profile/{self.animal.id}/')
        self.assertRedirects(response, '/profiles/')
        self.assertTrue(Animal.objects.filter(id=self.animal.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Only shelter admin can delete animal")

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
            adoption_status = "Available"
        )
    
    def test_view(self):
        response = self.client.get('/animals/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/view_animals.html')
        self.assertIn('animals', response.context)
        self.assertEqual(len(response.context['animals']), 1)


class AddUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name="Test Shelter1",
            registration_number="12345",
            website="http://example.com",
            description="A test shelter1."
        )
        self.image = SimpleUploadedFile(name='test_image.jpg', content=b"dummy image data", content_type='image/jpeg')
        self.animal = Animal.objects.create(
            shelter = self.shelter,
            name = "Sky",
            species = "Dog",
            breed = "Collie",
            age = 3,
            description = "A honey bunny",
            adoption_status = "Available",
            image = self.image
        )
        self.url = f'/animals/add-update/{self.animal.id}/'
        self.client.login(username='testuser', password='12345')

    def test_add_update_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/add_update.html')
        self.assertIsInstance(response.context['form'], UpdateForm)

    def test_add_update_view_post_valid_data(self):
        data = {
            'text': 'The animal is healthy and doing well.',
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, f'/animals/profile/{self.animal.id}/')

        self.assertEqual(Update.objects.count(), 1)
        update = Update.objects.first()
        self.assertEqual(update.animal, self.animal)
        self.assertEqual(update.text, 'The animal is healthy and doing well.')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Update added for '{self.animal.name}'.")

    def test_add_update_view_post_invalid_data(self):
        # Test POST request with invalid data
        data = {
            'text': '',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Error adding update - Check the form")

    def test_add_update_view_unauthorized_user(self):
        other_user = User.objects.create_user(username='otheruser', password='12345')
        self.client.login(username='otheruser', password='12345')
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/animals/profile/{self.animal.id}/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Only shelter admin can add update")

    def tearDown(self):
        if self.animal.image:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.animal.image.name))

        super().tearDown()


class EditUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='12345')
        self.shelter = Shelter.objects.create(admin=self.user, name='Test Shelter', registration_number='123456789', description='A test shelter')
        self.image = SimpleUploadedFile(name='test_image.jpg', content=b"dummy image data", content_type='image/jpeg')
        self.animal = Animal.objects.create(shelter=self.shelter, name='Test Animal', species='Dog', age=4, image=self.image)
        self.update = Update.objects.create(animal=self.animal, text='Initial update')
        self.url = f'/animals/edit-update/{self.update.id}/'

    def test_edit_update_view_get(self):
        self.client.login(username='admin', password='12345')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/edit_update.html')
        self.assertContains(response, 'Initial update')

    def test_edit_update_view_as_other_user(self):
        self.other_user = User.objects.create_user(username='other', password='12345')
        self.client.login(username='other', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Only shelter admin can edit this update")

    def test_edit_update_post_valid(self):
        self.client.login(username='admin', password='12345')
        response = self.client.post(self.url, {'text': 'Updated text'})

        self.update.refresh_from_db()
        self.assertEqual(self.update.text, 'Updated text')
        self.assertRedirects(response, f'/animals/profile/{self.update.animal.id}/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Update for '{self.animal.name}' edited")

    def test_edit_update_post_invalid(self):
        self.client.login(username='admin', password='12345')
        response = self.client.post(self.url, {'text': ''})  # Invalid data

        # Should rerender the form
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/edit_update.html')
        self.assertFalse(response.context['form'].is_valid())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Error editing update - Check the form")
    
    def tearDown(self):
        if self.animal.image:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.animal.image.name))

        super().tearDown()


class DeleteUpdateViewTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='adminuser', password='12345')
        self.shelter = Shelter.objects.create(admin=self.admin_user, name='Test Shelter', registration_number='12345', description='Test Shelter Description')
        self.image = SimpleUploadedFile(name='test_image.jpg', content=b"dummy image data", content_type='image/jpeg')
        self.animal = Animal.objects.create(shelter=self.shelter, name='Test Animal', species='Dog', age=3, image=self.image)
        self.update = Update.objects.create(animal=self.animal, text="This is an animal update.")
        self.url = f'/animals/delete-update/{self.update.id}/'

    def test_delete_update_as_admin(self):
        self.client.login(username='adminuser', password='12345')
        response = self.client.post(self.url)

        self.assertRedirects(response, f'/animals/profile/{self.update.animal.id}/')
        self.assertFalse(Update.objects.filter(id=self.update.id).exists())

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Update for '{self.animal.name}' deleted")
        self.assertEqual(messages[0].level_tag, 'success')

    def test_delete_update_as_non_admin(self):
        self.other_user = User.objects.create_user(username='otheruser', password='12345')
        self.client.login(username='otheruser', password='12345')
        response = self.client.post(self.url)

        self.assertRedirects(response, f'/animals/profile/{self.animal.id}/')
        self.assertTrue(Update.objects.filter(id=self.update.id).exists())

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Only shelter admin can delete this update")
        self.assertEqual(messages[0].level_tag, 'error')

    def test_delete_update_with_get_request(self):
        self.client.login(username='adminuser', password='12345')
        response = self.client.get(self.url)

        self.assertRedirects(response, f'/animals/profile/{self.animal.id}/')
        self.assertTrue(Update.objects.filter(id=self.update.id).exists())
    
    def tearDown(self):
        if self.animal.image:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.animal.image.name))

        super().tearDown()


# Models
class AnimalModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(admin=self.user, name="Test Shelter", registration_number="123456789", description="A test shelter")
        self.animal = None
    
    def test_animal_creation(self):
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            breed="Labrador",
            age=3,
            description="A friendly dog",
            adoption_status="Available",
            image = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
    
        )
        self.assertEqual(self.animal.name, "Test Animal")
        self.assertEqual(self.animal.species, "Dog")
        self.assertEqual(self.animal.breed, "Labrador")
        self.assertEqual(self.animal.age, 3)
        self.assertEqual(self.animal.description, "A friendly dog")
        self.assertEqual(self.animal.adoption_status, "Available")
        self.assertEqual(self.animal.shelter, self.shelter)
        self.assertTrue(self.animal.image)

    def test_string_representation(self):
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            age=3
        )
        expected_string = f"{self.animal.name} - {self.shelter}"
        self.assertEqual(str(self.animal), expected_string)
    
    def test_animal_without_optional_fields(self):
        # Animal instance without optional fields
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Cat",
            age=2
        )
        self.assertIsNone(self.animal.fosterer)
        self.assertIsNone(self.animal.breed)
        self.assertIsNone(self.animal.description)
        self.assertEqual(self.animal.adoption_status, "Available")  # Default status

    # def test_animal_missing_required_fields(self):
    #     with self.assertRaises(IntegrityError):
    #         Animal.objects.create(shelter=self.shelter)
    
    def tearDown(self):
        if self.animal.image:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.animal.image.name))

        super().tearDown()


class UpdateModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name="Test Shelter",
            registration_number="123456789",
            description="A test shelter"
        )
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            age=3
        )

    def test_update_creation(self):
        update = Update.objects.create(
            animal=self.animal,
            text="This is a test update."
        )
        self.assertEqual(update.animal, self.animal)
        self.assertEqual(update.text, "This is a test update.")
        self.assertTrue(isinstance(update.created_at, datetime))

    def test_str_method(self):
        update = Update.objects.create(
            animal=self.animal,
            text="This is a test update."
        )
        expected_str = f'Update for {self.animal.name} on {update.created_at.strftime("%Y-%m-%d")}'
        self.assertEqual(str(update), expected_str)

    def test_related_name(self):
        update1 = Update.objects.create(
            animal=self.animal,
            text="First update."
        )
        update2 = Update.objects.create(
            animal=self.animal,
            text="Second update."
        )
        # Check that the animal has two updates
        self.assertEqual(self.animal.updates.count(), 2)
        # Check that the updates are correctly related to the animal
        self.assertIn(update1, self.animal.updates.all())
        self.assertIn(update2, self.animal.updates.all())
