from django.test import TestCase


class HomeViewTests(TestCase):
    """ Unit tests for Home app view """
    def test_index_view(self):
        """ Test home page renders correct page """
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/index.html')