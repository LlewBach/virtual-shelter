from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.admin.sites import site
from .admin import ProfileAdmin


class ProfileModelTest(TestCase):
    def test_profile_creation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        self.assertTrue(Profile.objects.filter(user=user).exists())
    
    def test_profile_str(self):
        user = User.objects.create_user(username='testuser', password='12345')
        profile = Profile.objects.get(user=user)
        self.assertEqual(str(profile), 'testuser Profile')


class ProfileAdminTest(TestCase):
    def test_profile_admin_registration(self):
        self.assertIn(Profile, site._registry)

    def test_profile_admin_list_display(self):
        profile_admin = ProfileAdmin(Profile, site)
        self.assertEqual(profile_admin.list_display, ('user', 'role'))


    

