class IConnector:
    def fetch_posts(self): raise NotImplementedError
    def convert_to_socialpost(self, events, social_posts): raise NotImplementedError