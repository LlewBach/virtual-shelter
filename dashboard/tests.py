import os
from django.conf import settings
from django.utils import timezone
from django.test import TestCase
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
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
        self.assertEqual(response.context['profile'], self.user.profile)

    def test_dashboard_view_with_success_payment_status(self):
        """Test accessing the dashboard with a successful payment status."""
        response = self.client.get('/dashboard/?payment_status=success')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "Payment successful! Received 100 tokens.")
        self.assertEqual(messages[0].tags, "success")

    def test_dashboard_view_with_cancel_payment_status(self):
        """Test accessing the dashboard with a canceled payment status."""
        response = self.client.get('/dashboard/?payment_status=cancel')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "Payment canceled. No tokens added.")
        self.assertEqual(messages[0].tags, "error")
    
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
            adoption_status='Available',
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
        self.animal.refresh_from_db()
        self.assertEqual(Sprite.objects.count(), 1)
        self.assertEqual(self.animal.adoption_status, 'Fostered')
        self.assertEqual(self.animal.fosterer, self.user.profile)
        self.assertRedirects(response, '/dashboard/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"'{self.animal.name}' fostered")

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

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Error fostering - Check the form")

    def test_redirect_if_user_is_shelter_admin(self):
        """
        Test that a shelter admin cannot foster an animal.
        """
        self.user.profile.role = 'shelter_admin'
        self.user.profile.save()
        response = self.client.get(f'/dashboard/select-sprite/{self.animal.id}/')
        self.assertRedirects(response, '/animals/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You cannot foster this animal")

    def test_redirect_if_user_is_already_fosterer(self):
        """
        Test that a user who is already the fosterer cannot foster the same animal again.
        """
        self.animal.fosterer = self.user.profile
        self.animal.save()
        response = self.client.get(f'/dashboard/select-sprite/{self.animal.id}/')
        self.assertRedirects(response, '/animals/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You cannot foster this animal")

    
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
            adoption_status='Available'
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
        self.assertEqual(self.animal.fosterer, None)
        self.assertEqual(self.animal.adoption_status, 'Available')
        self.assertRedirects(response, '/dashboard/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "'Test Animal' returned to shelter")

    def test_unauthorized_sprite_deletion(self):
        other_user = User.objects.create_user(username='otheruser', password='12345')
        self.client.login(username='otheruser', password='12345')

        url = f'/dashboard/delete-sprite/{self.sprite.id}/'
        response = self.client.post(url)

        self.assertEqual(Sprite.objects.count(), 1)
        self.assertRedirects(response, '/dashboard/')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Not authorized to delete this sprite")        


class UpdateStatusViewTests(TestCase):
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
    
    @patch.object(Sprite, 'update_status')
    def test_update_status_view(self, mock_update_status):
        url = f'/dashboard/sprite/{self.sprite.id}/update-status/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'satiation': self.sprite.satiation,
            'current_state': self.sprite.current_state,
            'time_standing': self.sprite.time_standing,
            'time_running': self.sprite.time_running
            })
        mock_update_status.assert_called_once()


class FeedSpriteTestCase(TestCase):
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
            url='husky/one',
            satiation=50,
        )
        self.url = f'/dashboard/sprite/{self.sprite.id}/feed/'
        self.user.profile.tokens = 100
        self.user.profile.save()

    def test_feed_sprite_view(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])

        # Check if the sprite's satiation was increased by 5
        self.sprite.refresh_from_db()
        self.assertEqual(self.sprite.satiation, 55)
        self.assertEqual(response_data['satiation'], self.sprite.satiation)

        # Check if the tokens were deducted
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.tokens, 99)
        self.assertEqual(response_data['tokens'], self.user.profile.tokens)
    
    def test_sufficient_tokens(self):
        self.user.profile.tokens = 0
        self.user.profile.save()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertFalse(response_data['success'])

    def test_feed_sprite_max_satiation(self):
        self.sprite.satiation = 99
        self.sprite.save()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()

        # Check if the satiation is capped at 100
        self.sprite.refresh_from_db()
        self.assertEqual(self.sprite.satiation, 100)
        self.assertEqual(response_data['satiation'], 100)


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
        self.assertEqual(sprite.current_state, Sprite.States.STANDING)

    def test_string_representation(self):
        sprite = Sprite.objects.create(
            user=self.user,
            animal=self.animal
        )
        self.assertEqual(str(sprite), f"Sprite {sprite.id} for {sprite.animal.name}")

    def test_update_status(self):
        sprite = Sprite.objects.create(
            user=self.user,
            animal=self.animal,
            satiation=55,
        )
        sprite.update_status()
        # Since satiation is > 50, current state should be RUNNING
        self.assertEqual(sprite.current_state, Sprite.States.RUNNING)

        Sprite.objects.filter(id=sprite.id).update(last_checked=timezone.now() - timezone.timedelta(minutes=10))

        # Doesn't work
        # sprite.last_checked = timezone.now() - timezone.timedelta(minutes=10)
        # sprite.save()

        sprite.refresh_from_db()
        sprite.update_status()

        # Since 10 minutes have passed, satiation should decrease by 10
        self.assertEqual(sprite.satiation, 45)

        # Since satiation is < 50, current state should change to STANDING
        self.assertEqual(sprite.current_state, Sprite.States.STANDING)

        # Ensure last_checked is updated to now
        self.assertAlmostEqual(sprite.last_checked, timezone.now(), delta=timezone.timedelta(seconds=1))

    def test_update_status_no_negative_satiation(self):
        sprite = Sprite.objects.create(
            user=self.user,
            animal=self.animal,
            satiation=5,
        )

        Sprite.objects.filter(id=sprite.id).update(last_checked=timezone.now() - timezone.timedelta(minutes=10))
        sprite.refresh_from_db()

        sprite.update_status()
        # Satiation should not go below 0
        self.assertEqual(sprite.satiation, 0)

    def test_update_status_updates_last_checked(self):
        now = timezone.now()
        sprite = Sprite.objects.create(
            user=self.user,
            animal=self.animal,
        )

        Sprite.objects.filter(id=sprite.id).update(last_checked=timezone.now() - timezone.timedelta(minutes=10))
        sprite.refresh_from_db()

        sprite.update_status()
        self.assertEqual(sprite.last_checked.replace(microsecond=0), now.replace(microsecond=0))

    def test_update_status_resets_state_timers(self):
        now = timezone.now()
        sprite = Sprite.objects.create(
            user=self.user,
            animal=self.animal,
            time_standing=30,
            time_running=20
        )

        Sprite.objects.filter(id=sprite.id).update(last_checked=timezone.now() - timezone.timedelta(days=1))
        sprite.refresh_from_db()

        sprite.update_status()

        self.assertEqual(sprite.time_standing, 0)
        self.assertEqual(sprite.time_running, 0)