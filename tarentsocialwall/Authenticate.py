from passlib.hash import sha256_crypt

from tarentsocialwall import SocialWallPostFetcher
from tarentsocialwall.IAuthenticate import IAuthenticate

mongoClient = SocialWallPostFetcher.mongoClient


class Authenticate(IAuthenticate):
    def authenticate_user(self, username, password):
        user = mongoClient.read_user(username)

        if user is None:
            return None

        verify_result = sha256_crypt.verify(password, user['password'])

        if verify_result:
            return user
