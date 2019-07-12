import datetime
from unittest import TestCase

from tarentsocialwall.GoogleCalendarConnector import GoogleCalendarConnector


class TestGoogleCalendarConnector(TestCase):

    service = None

    def setUp(self):
        self.service = GoogleCalendarConnector()

    def test_convert_to_socialpost_from_event_empty(self):
        event = []
        social_posts = []  # type: List[SocialPost]

        self.service.convert_to_socialpost(event, social_posts)

        self.assertTrue(len(event) == len(social_posts))

    def test_convert_to_socialpost_from_event_with_exception(self):
        social_posts = []  # type: List[SocialPost]

        self.service.convert_to_socialpost(None, social_posts)

        self.assertTrue(0 == len(social_posts))

    def test_convert_to_socialpost_from_event_corectly(self):

        event = {}

        event['id'] = '123456'
        event['summary'] = 'test'
        event['extern'] = 'test'
        event['status'] = 'confirmed'
        event['start'] = {}
        event['start']['dateTime'] = datetime.datetime.now().isoformat()
        event['end'] = {}
        event['end']['dateTime'] = datetime.datetime.now().isoformat()

        events = [event]
        social_posts = []

        self.service.convert_to_socialpost(events, social_posts)
        self.assertTrue(len(social_posts) == 1)
        social_post = social_posts[0]
        externalId = social_post.externalId
        self.assertTrue(externalId == '123456')
