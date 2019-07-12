import json
from datetime import datetime, timedelta
from typing import List

import oauth2 as oauth

from tarentsocialwall.IConnector import IConnector
from tarentsocialwall.SocialPost import SocialPost
from tarentsocialwall.Util import Util


class TwitterConnector(IConnector):
    data = None
    client = None

    try:
        root = Util.get_credentials_folder(__file__)
        json_file = str(root) + "/credentials/twitter.json"

        data = Util.get_json_file_from_file_path(json_file)
    except Exception as ex:
        print('TwitterConnector: File not found %s' % ex)

    if data is not None:
        try:
            consumer_key = data['consumer_key']
            consumer_secret = data['consumer_secret']
            access_key = data['access_key']
            access_secret = data['access_secret']
            timeline_endpoint = data['timeline_endpoint']

            consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
            access_token = oauth.Token(key=access_key, secret=access_secret)
            client = oauth.Client(consumer, access_token)
            print('TwitterConnector is ready')
        except Exception as ex:
            print('TwitterConnector is no ready %s' % ex)
            client = None

    twitterDateFormat = "%a %b %d %H:%M:%S +%f %Y"

    def fetch_posts(self) -> List[SocialPost]:

        social_posts = []  # type: List[SocialPost]

        if self.client is None:
            return social_posts

        response, data = self.client.request(self.timeline_endpoint)

        twitter_posts = json.loads(data)

        for twitter_post in twitter_posts:

            if twitter_post == "errors":
                print(twitter_post)
                continue

            social_post = SocialPost()
            social_post.text = twitter_post["full_text"]
            social_post.externalId = twitter_post["id"]

            entities = twitter_post["entities"]
            if "media" in entities:
                media = entities["media"]
                media_urls = []
                if media is not None:
                    for medium in media:
                        media_urls.append(medium["media_url_https"])
                social_post.mediaURLs = media_urls

            created_date = datetime.strptime(twitter_post["created_at"], self.twitterDateFormat)

            social_post.created = Util.convert_date_to_UTC_time_stamp(created_date)
            social_post.validTo = Util.convert_date_to_UTC_time_stamp(created_date + timedelta(weeks=3))
            social_post.validFrom = Util.convert_date_to_UTC_time_stamp(created_date)
            social_post.source = "twitter"
            social_posts.append(social_post)

        return social_posts
