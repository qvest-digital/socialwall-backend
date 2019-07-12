import datetime
from unittest import TestCase

from tarentsocialwall.WordpressConnector import WordpressConnector


class TestWordpressConnector(TestCase):
    service = None

    def setUp(self):
        self.service = WordpressConnector()


    def test_convert_to_socialpost_from_event_empty(self):
        event = []
        social_posts = []  # type: List[SocialPost]
        self.service.convert_to_socialpost(event, social_posts)

    def test_convert_to_socialpost_from_event_corectly(self):
        self.service.access_token = "i have access"
        event = {}

        event['id'] = '123456'

        event['title'] = {}
        event['title']['rendered'] = 'test'
        event['content'] = {}
        event['content']['rendered'] = 'test'
        event['date'] = datetime.datetime.now().strftime(self.service.wordpressDateFormat)

        events = [event]

        social_posts = []

        self.service.convert_to_socialpost(events, social_posts)
        self.assertTrue(len(social_posts) == 1)
        social_post = social_posts[0]
        externalId = social_post.externalId
        self.assertTrue(externalId == '123456')