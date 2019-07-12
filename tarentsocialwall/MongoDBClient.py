from datetime import datetime

from passlib.handlers.sha2_crypt import sha256_crypt
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from tarentsocialwall.SocialPost import SocialPost
from tarentsocialwall.User import User
from tarentsocialwall.Util import Util


class MongoDBClient:

    __instance = None
    @staticmethod
    def getInstance():
        """ Static access method. """
        if MongoDBClient.__instance == None:
            MongoDBClient()

    client = None
    db = None

    def __init__(self, uri):
        # connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
        self.client = MongoClient(uri)
        self.db = self.client.socialPosts

        try:
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
        except ConnectionFailure:
            print("Server not available")

        if MongoDBClient.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MongoDBClient.__instance = self

    # write social_post into mongo
    def write_social_post(self, social_post: SocialPost):

        existing_dict = None

        try:
            existing_dict = self.db.socialPosts.find_one({'externalId': social_post.externalId})
        except Exception as ex:
            print(ex)
            existing_dict = None

        if existing_dict is None:
            self.db.socialPosts.insert_one(social_post.__dict__)
        else:
            update_identifier = {'externalId': social_post.externalId, 'source': social_post.source}
            self.db.socialPosts.replace_one(update_identifier, social_post.__dict__)
        return 0

    # read random social_post from mongo
    def get_random_social_post(self) -> SocialPost:

        timestamp_var = datetime.utcnow().timestamp()

        doc = list(self.db.socialPosts.aggregate([{'$sample': {'size': 20}},
                                                  {'$match': {'validFrom': {'$lte': timestamp_var},
                                                              'validTo': {'$gte': timestamp_var}}}]))
        if len(doc) == 0:
            return None
        else:
            doc = doc[0]

        print(doc)
        if doc is None:
            return None

        social_post = SocialPost()
        social_post.set_dictionary(doc)
        return social_post

    # read custom social_post from mongo
    def get_custom_social_post(self):

        doc = list(self.db.socialPosts.aggregate([{'$match': {'source': 'custom post'}}]))

        print(list(doc))
        if doc is None:
            return None

        social_post_list = []
        for post in doc:
            custom_post_item = SocialPost()
            custom_post_item.set_dictionary(post)
            social_post_list.append(custom_post_item)

        return social_post_list

    def delete_post(self, external_id):
        removed = self.db.socialPosts.delete_one({'externalId': external_id})
        print(removed)

    def write_access_token(self, access_token, source):
        existing_dict = self.db.storeAccessToken.find_one({'source': access_token})
        if existing_dict is None:
            identifier = {'access_token': access_token, 'source': source}
            self.db.storeAccessToken.insert_one(identifier)
        else:
            update_identifier = {'access_token': access_token, 'source': source}
            self.db.storeAccessToken.replace_one(update_identifier, access_token)
        return 0

    def read_access_token(self, source):
        existing_dict = self.db.storeAccessToken.find_one({'source': source})
        return existing_dict

    def get_google_calendar_posts(self):

        timestamp_var = datetime.utcnow().timestamp()

        doc = list(self.db.socialPosts.aggregate([
            {'$match': {'validFrom': {'$lte': timestamp_var},
                        'validTo': {'$gte': timestamp_var},
                        'source': 'Google calendar'}},
            {'$sort': {'start': 1}}
        ]))

        if doc is None:
            return None

        social_post_list = []
        for post in doc:
            custom_post_item = SocialPost()
            custom_post_item.set_dictionary(post)
            social_post_list.append(custom_post_item)

        return social_post_list

    def get_users(self):
        users_db = list(self.db.socialwall_users.find())
        if users_db is None:
            return None

        users = []

        for item in users_db:
            if item['username'] is not 'admin':
                user = User()
                user.set_dictionary(item)
                users.append(user)

        return users

    def read_user(self, username):
        return self.db.socialwall_users.find_one({'username': username})

    def write_user(self, user: User):
        username_dict = self.db.socialwall_users.find_one({'username': user.username})
        if username_dict is None:
            self.db.socialwall_users.insert_one(user.__dict__)
        else:
            update_identifier = {'username': user.username}
            self.db.socialwall_users.replace_one(update_identifier, user.__dict__)
        return 0

    def delete_user(self, user: User):
        self.db.socialwall_users.delete_one({'username': user['username']})

    def init_admin(self):
        random_string = Util.randomString()

        user = User()
        user.username = 'admin'
        user.password = sha256_crypt.hash(random_string)
        print("Admin password is '%s'" % random_string)
        user.firstname = 'admin'
        user.lastname = 'admin'
        self.write_user(user)
