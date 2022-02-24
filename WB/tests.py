from django.test import TestCase
from django.urls import reverse


# Create your tests here.


class TestViews(TestCase):

    def test_index(self):  # test index page (world bank graph making page)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_graph(self):  # test graph page with example GET request that returns no data
        response = self.client.get(reverse('graph'),
                                   data={'states': 'AFG', 'metrics': 'SP.POP.TOTL', 'year1': '2019', 'year2': '2021',
                                         'title': '', 'x_label': '', 'y_label': '', 'auto_scale': '1'})
        self.assertEqual(response.status_code, 200)

    # def test_home(self):  # test home page
    #     response = self.client.get(reverse('home'))
    #     self.assertEqual(response.status_code, 200)
