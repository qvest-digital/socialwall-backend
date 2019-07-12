class SocialPost:

    def set_dictionary(self, dictionary):
        for key in dictionary:
            if key != '_id':
                self.__dict__[key] = dictionary[key]
