from django.test import TestCase


class DashboardViewTests(TestCase):
    def test_dashboard_view_status_code(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')
        