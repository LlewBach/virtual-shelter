import os
from django.conf import settings
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from shelters.models import Shelter
from animals.models import Animal
from .models import Sprite
from .forms import SpriteForm


# Views
class DashboardViewTests(TestCase):
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
            description="A friendly dog",
            adoption_status='available',
            image=self.image
        )
        self.sprite = Sprite.objects.create(
            user=self.user,
            animal=self.animal,
            breed=Sprite.BreedChoices.HUSKY,
            colour=Sprite.ColourChoices.ONE,
            url='husky/one'
        )

    def test_dashboard_view_get(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')
        self.assertEqual(list(response.context['sprites']), [self.sprite])
    
    def tearDown(self):
        if self.animal.image:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.animal.image.name))
        super().tearDown()


class SelectSpriteViewTests(TestCase):
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
            description="A friendly dog",
            adoption_status='available',
            image=self.image
        )

    def test_select_sprite_get(self):
        """
        Test the GET request to ensure the form is displayed.
        """
        response = self.client.get(f'/dashboard/select-sprite/{self.animal.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/select_sprite.html')
        self.assertIsInstance(response.context['form'], SpriteForm)

    def test_select_sprite_post_valid(self):
        """
        Test a valid POST request to ensure the sprite is created.
        """
        url = f'/dashboard/select-sprite/{self.animal.id}/'
        data = {
            'breed': Sprite.BreedChoices.HUSKY,
            'colour': Sprite.ColourChoices.ONE
        }
        response = self.client.post(url, data)
        self.assertEqual(Sprite.objects.count(), 1)
        self.assertRedirects(response, '/dashboard/')

    def test_select_sprite_post_invalid(self):
        """
        Test an invalid POST request to ensure the sprite is not created and errors are shown.
        """
        url = f'/dashboard/select-sprite/{self.animal.id}/'
        data = {
            'breed': 'nonexistent',
            'colour': 'nonexistent'
        }
        response = self.client.post(url, data)
        self.assertEqual(Sprite.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertFalse(response.context['form'].is_valid())
        self.assertTemplateUsed(response, 'dashboard/select_sprite.html')
    
    def tearDown(self):
        if self.animal.image:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.animal.image.name))
        super().tearDown()


class DeleteSpriteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(admin=self.user, name="Test Shelter", registration_number="123456789", description="A test shelter")
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            age=4,
            description="A friendly dog",
            adoption_status='available'
        )
        self.sprite = Sprite.objects.create(
            user=self.user,
            animal=self.animal,
            breed=Sprite.BreedChoices.HUSKY,
            colour=Sprite.ColourChoices.ONE,
            url='husky/one'
        )

    def test_sprite_deletion(self):
        self.assertEqual(Sprite.objects.count(), 1)
        
        url = f'/dashboard/delete-sprite/{self.sprite.id}/'
        response = self.client.post(url)
        self.assertEqual(Sprite.objects.count(), 0)
        self.assertRedirects(response, '/dashboard/')


# Models
class SpriteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.shelter = Shelter.objects.create(admin=self.user, name="Test Shelter", registration_number="123456789", description="A test shelter")
        self.animal = Animal.objects.create(
            shelter=self.shelter,
            name="Test Animal",
            species="Dog",
            age=4,
            description="A friendly dog",
            adoption_status='available'
        )

    def test_sprite_creation(self):
        sprite = Sprite.objects.create(
            user=self.user,
            animal=self.animal,
            breed=Sprite.BreedChoices.HUSKY,
            colour=Sprite.ColourChoices.ONE,
            url='husky/one'
        )

        self.assertEqual(sprite.user, self.user)
        self.assertEqual(sprite.animal, self.animal)
        self.assertEqual(sprite.breed, "husky")
        self.assertEqual(sprite.colour, "one")
        self.assertIsNotNone(sprite.created_at)

    def test_sprite_sheet_choices(self):
        # Test creating sprites with all available choices.
        for choice in Sprite.BreedChoices.choices:
            sprite = Sprite.objects.create(
                user=self.user,
                animal=self.animal,
                breed=choice[0],
                colour="one"
            )
            self.assertEqual(sprite.breed, choice[0])
        
        for choice in Sprite.ColourChoices.choices:
            sprite = Sprite.objects.create(
                user=self.user,
                animal=self.animal,
                breed="husky",
                colour=choice[0]
            )
            self.assertEqual(sprite.colour, choice[0])

    def test_sprite_defaults(self):
        sprite = Sprite.objects.create(
            user=self.user,
            animal=self.animal
        )
        self.assertEqual(sprite.breed, Sprite.BreedChoices.HUSKY)
        self.assertEqual(sprite.colour, Sprite.ColourChoices.ONE)

    def test_string_representation(self):
        sprite = Sprite.objects.create(
            user=self.user,
            animal=self.animal
        )
        self.assertEqual(str(sprite), f"Sprite {sprite.id} for {sprite.animal.name}")
