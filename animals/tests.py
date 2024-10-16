import os
from django.conf import settings
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from django.contrib.auth.models import User
from shelters.models import Shelter
from .models import Animal, Update
from animals.forms import AnimalForm, UpdateForm
from datetime import datetime


# Views
class AddAnimalViewTest(TestCase):
    """
    Test cases for the Add Animal view.

    Ensures correct behavior when adding a new animal, including handling
    redirects for users without shelters and validation for valid/invalid POST
    requests.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user, shelter, and logging
        the user in.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
            )
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name="Test Shelter",
            registration_number="123456789",
            description="A test shelter"
            )
        self.client.login(username='testuser', password='12345')

    def test_redirect_if_no_shelter(self):
        """
        Test redirect behavior when the user has no associated shelter.
        """
        self.shelter.delete()
        response = self.client.get('/animals/add/')
        self.assertRedirects(response, '/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You aren't a shelter admin")
        self.assertEqual(messages[0].tags, 'error')

    def test_add_animal_post_request(self):
        """
        Test adding an animal with a valid POST request.
        """
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
        Test an invalid POST request to ensure the form re-renders with errors.
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
    """
    Test cases for the Animal profile view.

    Ensures correct behavior when accessing the animal's profile page with
    valid and invalid IDs.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user, shelter, animal, and
        uploading an image.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
            )
        self.client.login(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name="Test Shelter",
            registration_number="123456789",
            description="A test shelter"
            )
        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b"dummy image data",
            content_type='image/jpeg'
            )
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            age=4,
            adoption_status='Available',
            image=self.image
        )

    def test_profile_view_with_valid_id(self):
        """
        Test accessing the animal's profile page with a valid animal ID.
        """
        url = f'/animals/profile/{self.animal.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/profile.html')
        self.assertContains(response, self.animal.name)

    def test_profile_view_with_invalid_id(self):
        """
        Test accessing the animal's profile page with an invalid animal ID,
        expecting a redirect.
        """
        url = f'/animals/profile/999/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Animal not found")
        self.assertEqual(messages[0].level_tag, 'error')

    def tearDown(self):
        """
        Clean up by deleting the uploaded image after the test.
        """
        if self.animal.image:
            os.remove(
                os.path.join(settings.MEDIA_ROOT, self.animal.image.name)
                )

        super().tearDown()


class EditProfileViewTest(TestCase):
    """
    Test cases for the Edit Animal Profile view.

    Ensures proper behavior for authorized and unauthorized users, as well as
    handling of valid and invalid form submissions.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user, shelter, and animal,
        and logging in the user.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
            )
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name="Test Shelter",
            registration_number="123456789",
            description="A test shelter"
            )
        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b"dummy image data",
            content_type='image/jpeg'
            )
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
        """
        Test that a user who is not the shelter admin cannot edit the animal's
        profile.
        """
        other_user = User.objects.create_user(
            username='otheruser',
            password='12345'
            )
        self.client.login(username='otheruser', password='12345')

        response = self.client.get(f'/animals/edit-profile/{self.animal.id}/')
        self.assertRedirects(response, '/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Only shelter admin can edit animal"
            )

    def test_edit_profile_view_get(self):
        """
        Test that the edit profile page renders correctly for authorized users.
        """
        url = f'/animals/edit-profile/{self.animal.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/edit_profile.html')
        self.assertIsInstance(response.context['form'], AnimalForm)
        self.assertEqual(response.context['form'].instance, self.animal)

    def test_edit_profile_view_post_valid(self):
        """
        Test submitting a valid POST request to update the animal's profile.
        """
        data = {
            'name': 'Updated Animal Name',
            'species': 'Dog',
            'age': 5,
            'description': 'A friendly dog',
            'adoption_status': 'Fostered'
        }
        response = self.client.post(
            f'/animals/edit-profile/{self.animal.id}/', data
            )

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
        """
        Test submitting an invalid POST request and ensuring the form is
        re-rendered with errors.
        """
        data = {
            'name': '',  # Name is required
            'species': 'Dog',
            'age': 4,
        }
        response = self.client.post(
            f'/animals/edit-profile/{self.animal.id}/', data
            )

        # Should rerender page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/edit_profile.html')
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('name', response.context['form'].errors)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Error saving animal - Check the form"
            )

    def tearDown(self):
        """
        Clean up by deleting the uploaded image after the test.
        """
        if self.animal.image:
            os.remove(
                os.path.join(settings.MEDIA_ROOT, self.animal.image.name)
                )

        super().tearDown()


class DeleteProfileViewTest(TestCase):
    """
    Test cases for deleting an animal profile.

    Ensures only the shelter admin can delete an animal and handles attempts by
    unauthorized users or invalid animal IDs.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user, shelter, and animal.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
            )
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
            age=4,
            description="A friendly dog",
            adoption_status='Available'
        )

    def test_delete_animal_profile_as_admin(self):
        """
        Test that a shelter admin can delete an animal profile successfully.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.post(
            f'/animals/delete-profile/{self.animal.id}/'
            )
        self.assertRedirects(response, '/')
        self.assertFalse(Animal.objects.filter(id=self.animal.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            f"Animal '{self.animal.name}' deleted."
            )

    def test_delete_animal_profile_as_non_admin(self):
        """
        Test that a user who is not the shelter admin cannot delete an animal
        profile.
        """
        other_user = User.objects.create_user(
            username='otheruser',
            password='12345'
            )
        self.client.login(username='otheruser', password='12345')
        response = self.client.post(
            f'/animals/delete-profile/{self.animal.id}/'
            )
        self.assertRedirects(response, '/profiles/')
        self.assertTrue(Animal.objects.filter(id=self.animal.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            "Only shelter admin can delete animal"
            )

    def test_delete_animal_profile_invalid_id(self):
        """
        Test attempting to delete an animal profile with an invalid ID,
        expecting a 404 response.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.post('/animals/delete-profile/999/')
        self.assertEqual(response.status_code, 404)


class ViewAnimalsViewTest(TestCase):
    """
    Test cases for the View Animals page.

    Ensures that animals are correctly displayed on the view animals page.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user, shelter, and animal.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
            )
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name="Test Shelter1",
            registration_number="12345",
            website="http://example.com",
            description="A test shelter1."
        )
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Sky",
            species="Dog",
            breed="Collie",
            age=3,
            description="A honey bunny",
            adoption_status="Available"
        )

    def test_view(self):
        """
        Test that the view animals page loads correctly and displays the
        animals.
        """
        response = self.client.get('/animals/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/view_animals.html')
        self.assertIn('animals', response.context)
        self.assertEqual(len(response.context['animals']), 1)


class AddUpdateViewTest(TestCase):
    """
    Test cases for the Add Update view.

    Ensures proper behavior when adding updates for animals, including valid
    and invalid form submissions, and unauthorized access.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user, shelter, animal, and
        logging in the user.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
            )
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name="Test Shelter1",
            registration_number="12345",
            website="http://example.com",
            description="A test shelter1."
        )
        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b"dummy image data",
            content_type='image/jpeg'
            )
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Sky",
            species="Dog",
            breed="Collie",
            age=3,
            description="A honey bunny",
            adoption_status="Available",
            image=self.image
        )
        self.url = f'/animals/add-update/{self.animal.id}/'
        self.client.login(username='testuser', password='12345')

    def test_add_update_view_get(self):
        """
        Test accessing the Add Update view with a GET request.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/add_update.html')
        self.assertIsInstance(response.context['form'], UpdateForm)

    def test_add_update_view_post_valid_data(self):
        """
        Test submitting valid data via a POST request to add an update.
        """
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
        self.assertEqual(
            str(messages[0]),
            f"Update added for '{self.animal.name}'."
            )

    def test_add_update_view_post_invalid_data(self):
        """
        Test submitting invalid data via a POST request to add an update.
        """
        data = {
            'text': '',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Error adding update - Check the form"
            )

    def test_add_update_view_unauthorized_user(self):
        """
        Test that an unauthorized user cannot add an update.
        """
        other_user = User.objects.create_user(
            username='otheruser',
            password='12345'
            )
        self.client.login(username='otheruser', password='12345')
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/animals/profile/{self.animal.id}/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Only shelter admin can add update")

    def tearDown(self):
        """
        Clean up by deleting the uploaded test image after the test.
        """
        if self.animal.image:
            os.remove(
                os.path.join(settings.MEDIA_ROOT, self.animal.image.name)
                )

        super().tearDown()


class EditUpdateViewTest(TestCase):
    """
    Test cases for the Edit Update view.

    Ensures proper behavior when editing an update for an animal, including
    handling authorized and unauthorized access, and valid and invalid form
    submissions.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user, shelter, animal, and
        update.
        """
        self.user = User.objects.create_user(
            username='admin',
            password='12345'
            )
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name='Test Shelter',
            registration_number='123456789',
            description='A test shelter'
            )
        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b"dummy image data",
            content_type='image/jpeg'
            )
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name='Test Animal',
            species='Dog',
            age=4,
            image=self.image
            )
        self.update = Update.objects.create(
            animal=self.animal,
            text='Initial update'
            )
        self.url = f'/animals/edit-update/{self.update.id}/'

    def test_edit_update_view_get(self):
        """
        Test accessing the Edit Update view with a GET request.
        """
        self.client.login(username='admin', password='12345')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/edit_update.html')
        self.assertContains(response, 'Initial update')

    def test_edit_update_view_as_other_user(self):
        """
        Test that a user who is not the shelter admin cannot access the Edit
        Update view.
        """
        self.other_user = User.objects.create_user(
            username='other',
            password='12345'
            )
        self.client.login(username='other', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Only shelter admin can edit this update"
            )

    def test_edit_update_post_valid(self):
        """
        Test submitting valid data via a POST request to edit the update.
        """
        self.client.login(username='admin', password='12345')
        response = self.client.post(self.url, {'text': 'Updated text'})

        self.update.refresh_from_db()
        self.assertEqual(self.update.text, 'Updated text')
        self.assertRedirects(
            response,
            f'/animals/profile/{self.update.animal.id}/'
            )

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"Update for '{self.animal.name}' edited"
            )

    def test_edit_update_post_invalid(self):
        """
        Test submitting invalid data (empty text) via a POST request to edit
        the update.
        """
        self.client.login(username='admin', password='12345')
        response = self.client.post(self.url, {'text': ''})  # Invalid data

        # Should rerender the form
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'animals/edit_update.html')
        self.assertFalse(response.context['form'].is_valid())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Error editing update - Check the form"
            )

    def tearDown(self):
        """
        Clean up by deleting the uploaded test image after the test.
        """
        if self.animal.image:
            os.remove(
                os.path.join(settings.MEDIA_ROOT, self.animal.image.name)
                )

        super().tearDown()


class DeleteUpdateViewTest(TestCase):
    """
    Test cases for deleting an animal update.

    Ensures that only the shelter admin can delete an update, and handles
    different request methods (POST and GET).
    """
    def setUp(self):
        """
        Set up the test environment by creating a shelter admin, shelter,
        animal, and update.
        """
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='12345'
            )
        self.shelter = Shelter.objects.create(
            admin=self.admin_user,
            name='Test Shelter',
            registration_number='12345',
            description='Test Shelter Description'
            )
        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b"dummy image data",
            content_type='image/jpeg'
            )
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name='Test Animal',
            species='Dog',
            age=3,
            image=self.image
            )
        self.update = Update.objects.create(
            animal=self.animal,
            text="This is an animal update."
            )
        self.url = f'/animals/delete-update/{self.update.id}/'

    def test_delete_update_as_admin(self):
        """
        Test that the shelter admin can successfully delete an update.
        """
        self.client.login(username='adminuser', password='12345')
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            f'/animals/profile/{self.update.animal.id}/'
            )
        self.assertFalse(Update.objects.filter(id=self.update.id).exists())

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"Update for '{self.animal.name}' deleted"
            )
        self.assertEqual(messages[0].level_tag, 'success')

    def test_delete_update_as_non_admin(self):
        """
        Test that a non-admin user cannot delete an update.
        """
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='12345'
            )
        self.client.login(username='otheruser', password='12345')
        response = self.client.post(self.url)

        self.assertRedirects(response, f'/animals/profile/{self.animal.id}/')
        self.assertTrue(Update.objects.filter(id=self.update.id).exists())

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Only shelter admin can delete this update")
        self.assertEqual(messages[0].level_tag, 'error')

    def test_delete_update_with_get_request(self):
        """
        Test that accessing the delete update view via a GET request does not
        delete the update.
        """
        self.client.login(username='adminuser', password='12345')
        response = self.client.get(self.url)

        self.assertRedirects(response, f'/animals/profile/{self.animal.id}/')
        self.assertTrue(Update.objects.filter(id=self.update.id).exists())

    def tearDown(self):
        """
        Clean up by deleting the uploaded test image after the test.
        """
        if self.animal.image:
            os.remove(
                os.path.join(settings.MEDIA_ROOT, self.animal.image.name)
                )

        super().tearDown()


# Models
class AnimalModelTest(TestCase):
    """
    Test cases for the Animal model.

    Ensures proper behavior for creating and managing Animal instances,
    including optional fields and string representation.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user, shelter, and
        initializing the animal instance to None.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
            )
        self.shelter = Shelter.objects.create(
            admin=self.user,
            name="Test Shelter",
            registration_number="123456789",
            description="A test shelter"
            )
        self.animal = None

    def test_animal_creation(self):
        """
        Test creating an Animal instance with all fields, including the image.
        """
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            breed="Labrador",
            age=3,
            description="A friendly dog",
            adoption_status="Available",
            image=SimpleUploadedFile(
                name='test_image.jpg',
                content=b'',
                content_type='image/jpeg'
                )
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
        """
        Test the string representation of an Animal instance.
        """
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            age=3
        )
        expected_string = f"{self.animal.name} - {self.shelter}"
        self.assertEqual(str(self.animal), expected_string)

    def test_animal_without_optional_fields(self):
        """
        Test creating an Animal instance without optional fields (breed,
        description, fosterer).
        """
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            age=2
        )
        self.assertIsNone(self.animal.fosterer)
        self.assertIsNone(self.animal.breed)
        self.assertIsNone(self.animal.description)
        self.assertEqual(self.animal.adoption_status, "Available")  # Default

    def tearDown(self):
        """
        Clean up by deleting the uploaded test image after the test.
        """
        if self.animal.image:
            os.remove(
                os.path.join(settings.MEDIA_ROOT, self.animal.image.name)
                )

        super().tearDown()


class UpdateModelTest(TestCase):
    """
    Test cases for the Update model.

    Ensures that updates can be created, the string representation is correct,
    and updates are properly related to animals.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user, shelter, and animal.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
            )
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
        """
        Test creating an update for an animal.
        """
        update = Update.objects.create(
            animal=self.animal,
            text="This is a test update."
        )
        self.assertEqual(update.animal, self.animal)
        self.assertEqual(update.text, "This is a test update.")
        self.assertTrue(isinstance(update.created_at, datetime))

    def test_str_method(self):
        """
        Test the string representation of an Update instance.
        """
        update = Update.objects.create(
            animal=self.animal,
            text="This is a test update."
        )
        expected_str = (
            f'Update for {self.animal.name} on '
            f'{update.created_at.strftime("%Y-%m-%d")}'
        )
        self.assertEqual(str(update), expected_str)

    def test_related_name(self):
        """
        Test that updates are correctly related to the animal using the
        related_name 'updates'.
        """
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
