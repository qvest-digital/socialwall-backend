import os

from tarentsocialwall.GoogleCalendarConnector import GoogleCalendarConnector
from tarentsocialwall.InstagramConnector import InstagramConnector
from tarentsocialwall.MongoDBClient import MongoDBClient
from tarentsocialwall.WordpressConnector import WordpressConnector

mongoClient = MongoDBClient(os.environ.get('DB'))
wordpressClient = WordpressConnector()
googleCalendarClient = GoogleCalendarConnector()
instagramConnector = InstagramConnector(mongoClient)

mongoClient.init_admin()


def fetch_posts_job():
    print("fetch_posts...")
    wordpress_posts = wordpressClient.fetch_posts()
    for wordpress_post in wordpress_posts:
        mongoClient.write_social_post(wordpress_post)

    google_calendar_posts = googleCalendarClient.fetch_posts()
    for google_calendar_post in google_calendar_posts:
        if google_calendar_post.status == 'cancelled':
            print('delete %s' % google_calendar_post.externalId)
            mongoClient.delete_post(google_calendar_post.externalId)
        else:
            mongoClient.write_social_post(google_calendar_post)

    insta_posts = instagramConnector.fetch_posts()
    for insta_post in insta_posts:
        mongoClient.write_social_post(insta_post)


# run once at startup, then at interval (see docker-compose)
fetch_posts_job()
