"""
    This class manage ldap connection and a check a user
"""
import os

import ldap

from tarentsocialwall.IAuthenticate import IAuthenticate
from tarentsocialwall.User import User


class AuthenticateLDAP(IAuthenticate):

    def authenticate_user(self, username, password):
        """Verifies credentials for username and password.
        Returns None on success or a string describing the error on failure
        # Adapt to your needs
        """
        LDAP_SERVER = os.environ.get('LDAP')
        # fully qualified AD user name
        LDAP_USERNAME = os.environ.get('LDAP_USER_URI') % username
        # your password
        LDAP_PASSWORD = password

        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        search_filter = os.environ.get('LDAP_FILTER') % username
        result = None


        try:
            # build a client
            ldap_client = ldap.initialize(LDAP_SERVER)
            # perform a synchronous bind
            ldap_client.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)
            result = ldap_client.search_s(os.environ.get('LDAP-BASE'), ldap.SCOPE_SUBTREE, search_filter, ['cn',] )

            ldap_client.unbind()
        except ldap.INVALID_CREDENTIALS:
            ldap_client.unbind()
            return None
        except ldap.SERVER_DOWN:
            return None
        except Exception as e:
            print(e)
            return None

        if result is None or len(result) == 0:
            return None

        user = User()
        user.username = username
        user.password = password


        return user
