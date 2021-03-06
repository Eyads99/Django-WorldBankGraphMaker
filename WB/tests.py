from django.test import TestCase
from django.urls import reverse


class TestViews(TestCase):

    def test_index(self):  # test index page (world bank graph making page)
        response = self.client.get(reverse('WB:index'))
        self.assertEqual(response.status_code, 200)

    def test_graph_no_data(self):  # test graph page with example GET request that returns no data
        response = self.client.get(reverse('WB:graph'),
                                   data={'states': 'ABW', 'metrics': 'AG.AGR.TRAC.NO', 'year1': '2019', 'year2': '2021',
                                         'title': '', 'xlabel': '', 'ylabel': '', 'auto_scale': '1', 'width': '35',
                                         'height': '7', 'black_white': '0'})
        self.assertEqual(response.status_code, 200)

    def test_graph_data(self):  # test graph page with example GET request that returns data
        response = self.client.get(reverse('WB:graph'),
                                   data={'states': 'EGY', 'metrics': 'NY.GDP.MKTP.CD', 'year1': '1960', 'year2': '2021',
                                         'title': '', 'xlabel': '', 'ylabel': '', 'auto_scale': '1', 'width': '35',
                                         'height': '7', 'black_white': '0'})
        self.assertEqual(response.status_code, 200)

    def test_black_white(self):
        response = self.client.get(reverse('WB:graph'),
                                   data={'states': 'EGY', 'metrics': 'NY.GDP.MKTP.CD', 'year1': '1960', 'year2': '2021',
                                         'title': '', 'xlabel': '', 'ylabel': '', 'auto_scale': '1', 'width': '35',
                                         'height': '7', 'black_white': '1'})
        self.assertEqual(response.status_code, 200)

    def test_multi_country(self):  # test graph page with multiple countries and a single metric
        response = self.client.get(reverse('WB:graph'),
                                   data={'states': ['EGY', 'USA'], 'metrics': 'NY.GDP.MKTP.CD', 'year1': '1960',
                                         'year2': '2021',
                                         'title': '', 'xlabel': '', 'ylabel': '', 'auto_scale': '1', 'width': '35',
                                         'height': '7', 'black_white': '0'})
        self.assertEqual(response.status_code, 200)

    def test_multi_metric(self):  # test graph page with multiple metrics and a single country
        response = self.client.get(reverse('WB:graph'),
                                   data={'states': 'EGY', 'metrics': ['NY.GDP.MKTP.CD', 'AG.AGR.TRAC.NO'],
                                         'year1': '1960', 'year2': '2021',
                                         'title': '', 'xlabel': '', 'ylabel': '', 'auto_scale': '1', 'width': '35',
                                         'height': '7', 'black_white': '0'})
        self.assertEqual(response.status_code, 200)

    def test_multi(self):  # test multiple metrics and countries
        response = self.client.get(reverse('WB:graph'),
                                   data={'states': ['EGY', 'USA'],
                                         'metrics': ['NY.GDP.MKTP.KD.ZG', 'NY.GDP.PCAP.KD.ZG'],
                                         'year1': '1960', 'year2': '2021',
                                         'title': '', 'xlabel': '', 'ylabel': '', 'auto_scale': '1', 'width': '35',
                                         'height': '7', 'black_white': '0'})
        self.assertEqual(response.status_code, 200)

    # def test_home(self):  # test home page
    #     response = self.client.get(reverse('home'))
    #     self.assertEqual(response.status_code, 200)
