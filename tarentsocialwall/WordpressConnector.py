from datetime import datetime, timedelta
from typing import List

import requests

from tarentsocialwall.IConnector import IConnector
from tarentsocialwall.SocialPost import SocialPost
from tarentsocialwall.Util import Util


class WordpressConnector(IConnector):
    url = None

    try:
        root = Util.get_credentials_folder(__file__)
        json_file = str(root) + "/credentials/wordpress.json"
        data = Util.get_json_file_from_file_path(json_file)
        url = data['url']
    except Exception as ex:
        print('WordpressConnector: File not found %s' % ex)

    wordpressDateFormat = "%Y-%m-%dT%H:%M:%S"
    lastPostDate = datetime(2018, 1, 1, 0, 0, 0)  # format: 2018-09-20T00:00:00

    def fetch_posts(self) -> List[SocialPost]:
        social_posts = []  # type: List[SocialPost]
        wordpress_posts = None

        if self.url is None:
            print('WordpressConnector: url is none')
            return social_posts

        try:
            r = requests.get(self.url)
            wordpress_posts = r.json()
            print('WordpressConnector is ready')
        except Exception as ex:
            print('WordpressConnector is not ready %s' % ex)

        if wordpress_posts is None:
            return social_posts

        if len(wordpress_posts) > 0:
            self.convert_to_socialpost(wordpress_posts, social_posts)

        return social_posts

    def convert_to_socialpost(self, events, social_posts):
        for wordpress_post in events:
            social_post = SocialPost()
            social_post.text = wordpress_post["title"]["rendered"]
            social_post.description = wordpress_post["content"]["rendered"]
            social_post.externalId = wordpress_post["id"]

            # Tue Sep 18 07:44:20 +0000 2018

            created_date = datetime.strptime(wordpress_post["date"], self.wordpressDateFormat)

            social_post.created = Util.convert_date_to_UTC_time_stamp(created_date)
            social_post.validTo = Util.convert_date_to_UTC_time_stamp(created_date + timedelta(weeks=1))
            social_post.validFrom = Util.convert_date_to_UTC_time_stamp(created_date)
            social_post.source = "wordpress"
            social_posts.append(social_post)
