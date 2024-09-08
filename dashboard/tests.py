from django.test import TestCase
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
            sprite_sheet=Sprite.SpriteSheet.ONE
        )

    def test_dashboard_view_get(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')
        self.assertEqual(list(response.context['sprites']), [self.sprite])


class SelectSpriteViewTests(TestCase):
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
            'sprite_sheet': Sprite.SpriteSheet.ONE
        }
        response = self.client.post(url, data)
        self.assertEqual(Sprite.objects.count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/dashboard/')

    def test_select_sprite_post_invalid(self):
        """
        Test an invalid POST request to ensure the sprite is not created and errors are shown.
        """
        url = f'/dashboard/select-sprite/{self.animal.id}/'
        data = {
            'sprite_sheet': 'nonexistent'  # Invalid choice
        }
        response = self.client.post(url, data)
        self.assertEqual(Sprite.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        self.assertFalse(response.context['form'].is_valid())
        self.assertTemplateUsed(response, 'dashboard/select_sprite.html')


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
            animal=self.animal
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
            sprite_sheet=Sprite.SpriteSheet.ONE
        )

        self.assertEqual(sprite.user, self.user)
        self.assertEqual(sprite.animal, self.animal)
        self.assertEqual(sprite.sprite_sheet, Sprite.SpriteSheet.ONE)
        self.assertIsNotNone(sprite.created_at)

    def test_sprite_sheet_choices(self):
        # Test creating sprites with all available choices.
        for choice in Sprite.SpriteSheet.choices:
            sprite = Sprite.objects.create(
                user=self.user,
                animal=self.animal,
                sprite_sheet=choice[0]
            )
            self.assertEqual(sprite.sprite_sheet, choice[0])

    def test_sprite_defaults(self):
        sprite = Sprite.objects.create(
            user=self.user,
            animal=self.animal
        )
        self.assertEqual(sprite.sprite_sheet, Sprite.SpriteSheet.ONE)  # Default value check

    def test_string_representation(self):
        sprite = Sprite.objects.create(
            user=self.user,
            animal=self.animal,
            sprite_sheet=Sprite.SpriteSheet.ONE
        )
        self.assertEqual(str(sprite), f"Sprite {sprite.id} for {sprite.animal.name}")
