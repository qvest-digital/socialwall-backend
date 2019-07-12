from datetime import datetime, timedelta
from typing import List

import requests

from tarentsocialwall.IConnector import IConnector
from tarentsocialwall.SocialPost import SocialPost
from tarentsocialwall.Util import Util


class InstagramConnector(IConnector):
    mongo_client = None

    data = None
    try:
        root = Util.get_credentials_folder(__file__)
        json_file = str(root) + "/credentials/instagram.json"

        data = Util.get_json_file_from_file_path(json_file)
        insta_media_api = data['insta_media_api']
        access_token_url = data['access_token_url']
        scopes = ["basic", "public_content"]
        client_id = data['client_id']
        client_secret = data['client_secret']
        redirect_uri = data['redirect_uri']
    except Exception as ex:
        print('InstagramConnector: File not found %s' % ex)

    access_token = ''

    def __init__(self, mongo_client):
        try:
            self.mongo_client = mongo_client
            token = mongo_client.read_access_token("instagram")
            if token is None:
                print('Instagram: access token is not exist')
            else:
                self.access_token = token['access_token']
                print('Instagram: ready')
        except Exception as ex:
            print('InstagramConnector: access token is not exist %s' % ex)

    def init_instagram_connector(self, code):
        post_data = {"grant_type": "authorization_code",
                     "client_id": self.client_id,
                     "client_secret": self.client_secret,
                     "code": code,
                     "redirect_uri": self.redirect_uri}

        response_access_token = requests.post(self.access_token_url,
                                              data=post_data)
        token_json = response_access_token.json()
        self.access_token = token_json['access_token']
        self.mongo_client.write_access_token(self.access_token, "instagram")

    def fetch_posts(self) -> List[SocialPost]:

        social_posts = []  # type: List[SocialPost]

        if len(self.access_token) is 0:
            print('Instagram: access token is not exist')
            return []

        recent_media = requests.get(self.insta_media_api + self.access_token)
        data_json = recent_media.json()

        if(len(data_json['data']) > 0):
            self.convert_to_socialpost(data_json['data'], social_posts)

        return social_posts


    def convert_to_socialpost(self, events, social_posts):
        for insta_post in events:
            social_post = SocialPost()
            social_post.text = insta_post['caption']['text']
            social_post.externalId = insta_post['id']

            social_post.image = insta_post['images']['standard_resolution']['url']

            created_date = datetime.fromtimestamp(int(insta_post["created_time"]))

            social_post.created = Util.convert_date_to_UTC_time_stamp(created_date)

            social_post.validTo = Util.convert_date_to_UTC_time_stamp(created_date + timedelta(weeks=3))
            social_post.validFrom = Util.convert_date_to_UTC_time_stamp(created_date)
            social_post.source = "instagram"
            social_post.likes = insta_post['likes']['count']
            social_post.comments = insta_post['comments']['count']
            social_posts.append(social_post)

        return social_posts