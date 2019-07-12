from datetime import datetime, timedelta
from typing import List

import httplib2
from dateutil import parser
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from tarentsocialwall.IConnector import IConnector
from tarentsocialwall.SocialPost import SocialPost
from tarentsocialwall.Util import Util


class GoogleCalendarConnector(IConnector):
    # If modifying these scopes, delete the file token.json.
    SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'


    root = Util.get_credentials_folder(__file__)
    credentials_file = str(root) + "/credentials/google.json"

    data = Util.get_json_file_from_file_path(credentials_file)

    cal_id = data['calId']

    googleDateFormat = "%Y-%m-%dT%H:%M:%S%z"
    googleDateFormat2 = "%Y-%m-%dT%H:%M:%S.%fZ"

    def fetch_posts(self) -> List[SocialPost]:

        social_posts = []  # type: List[SocialPost]

        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, scopes=self.SCOPES)
            service = build('calendar', 'v3', http=credentials.authorize(httplib2.Http()))
            print('GoogleCalendarConnector is ready')
        except Exception as ex:
            print('GoogleCalendarConnector is not ready %s' % ex)
            return social_posts

        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId=self.cal_id, timeMin=now,
                                              maxResults=30, singleEvents=True,
                                              showDeleted=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        if events:
            self.convert_to_socialpost(events, social_posts)

        return social_posts

    def convert_to_socialpost(self, events, social_posts):
        if events is None:
            return []

        for event in events:
            try:
                social_post = SocialPost()
                social_post.text = event['summary']
                try:
                    social_post.created = Util.convert_date_to_UTC_time_stamp(
                        datetime.strptime(event['created'], self.googleDateFormat2))
                except Exception as ex:
                    print(ex)
                    social_post.created = int(datetime.utcnow().timestamp())

                if event['start'].get('dateTime') is not None:
                    social_post.start = parser.parse(event['start']['dateTime']).timestamp()
                    social_post.validFrom = (parser.parse(event['start']['dateTime']) - timedelta(weeks=3)).timestamp()
                else:
                    social_post.start = parser.parse(event['start']['date']).timestamp()
                    social_post.validFrom = (parser.parse(event['start']['date']) - timedelta(weeks=3)).timestamp()

                if event['end'].get('dateTime') is not None:
                    social_post.end = parser.parse(event['end']['dateTime']).timestamp()
                    social_post.validTo = parser.parse(event['end']['dateTime']).timestamp()
                else:
                    social_post.end = parser.parse(event['end']['date']).timestamp()
                    social_post.validTo = parser.parse(event['end']['date']).timestamp()

                social_post.externalId = event['id']

                if event.get('role') is not None:
                    social_post.role = event['role']

                location = event.get('location')

                if location is not None:
                    social_post.location = location
                else:
                    social_post.location = ''


                social_post.status = event['status']


                social_post.source = 'Google calendar'

                description = event.get('description')

                if description is not None:
                    social_post.description = description
                else:
                    social_post.location = ""

                social_posts.append(social_post)
            except Exception as ex:
                print('Exception in %s' % event)
                print(ex)
