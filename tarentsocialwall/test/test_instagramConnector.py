import datetime
from unittest import TestCase

from tarentsocialwall.InstagramConnector import InstagramConnector


class TestInstagramConnector(TestCase):

    service = None

    def setUp(self):
        self.service = InstagramConnector(None)


    def test_convert_to_socialpost_from_event_empty(self):
        event = []
        social_posts = []  # type: List[SocialPost]

        self.service.convert_to_socialpost(event, social_posts)

    def test_convert_to_socialpost_from_event_corectly(self):

        self.service.access_token = "i have access"
        event = {}

        event['id'] = '123456'

        event['caption'] = {}
        event['caption']['text'] = 'test'
        event['likes'] = {}
        event['likes']['count'] = '1'
        event['comments'] = {}
        event['comments']['count'] = '1'
        event['summary'] = 'test'
        event['extern'] = 'test'
        event['source'] = 'instagram'
        event['created_time'] = datetime.datetime.now().timestamp()
        event['images'] = {}
        event['images']['standard_resolution'] ={}
        event['images']['standard_resolution']['url'] = 'url to nirvana'

        events = [event]

        social_posts = []

        self.service.convert_to_socialpost(events, social_posts)
        self.assertTrue(len(social_posts) == 1)
        social_post = social_posts[0]
        externalId = social_post.externalId
        self.assertTrue(externalId == '123456')

