from django.test import TestCase
from django.urls import reverse


# Create your tests here.


class TestViews(TestCase):

    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
