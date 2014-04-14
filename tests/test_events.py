import sys
import unittest
import requests
import urlparse


class TestRoutes(unittest.TestCase):

    def setUp(self):
        try:
            self.__host = sys.argv[1]
        except IndexError:
            self.__host = 'http://docker'

    def make_url(self, path):
        return urlparse.urljoin(self.__host, path)

    def test_events_trackers(self):
        events = ['impression', 'click', 'creativeView', 'start', 'firstQuartile',
                  'midpoint', 'thirdQuartile', 'complete', 'mute', 'unmute', 'skip']

        for event in events:
            response = requests.get(self.make_url('/man/{}/'.format(event)))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.url, 'http://s.opendsp.com/1x1.gif')


if __name__ == '__main__':
    unittest.main()
