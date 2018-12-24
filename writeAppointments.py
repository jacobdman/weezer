from __future__ import print_function
import apiclient
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime

"""
share calendar with rivers@drivetimes-1532004541374.iam.gserviceaccount.com
"""

app_creds_dictionary = {"installed":{"client_id":","project_id":"drivetimes-1532004541374","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://accounts.google.com/o/oauth2/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"","redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}}

# Setup the Calendar API
SCOPES = 'https://www.googleapis.com/auth/calendar'
store = file.Storage('creds.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets(app_creds_dictionary, SCOPES)
    creds = tools.run_flow(flow, store)

service = build('calendar', 'v3', http=creds.authorize(Http()))

"""
Delete existing drives from Rivers Drive calendar
"""

# make a list of drives
driveList = []

# get the list of drives
page_token = None
while True:
  events = service.events().list(calendarId='8fi3dd5r0n9u5dsap2bnpkcd2o@group.calendar.google.com', pageToken=page_token).execute()
  for event in events['items']:
    driveList.append(event['id'])
  page_token = events.get('nextPageToken')
  if not page_token:
    break
# print(driveList)

# delete the drives
for driveID in driveList:
    service.events().delete(calendarId='8fi3dd5r0n9u5dsap2bnpkcd2o@group.calendar.google.com', eventId=driveID).execute()

"""
Write events to calendar
"""
def writeDrive(destination, start_int, end_int, tz_string, travelTypeString):
    travelTypeString = travelTypeString
    destination = destination
    # print('we\'re in the writeDrive function')
    # turns an int into a string
    start_string = datetime.datetime.fromtimestamp(start_int).strftime("%Y-%m-%dT%H:%M:%S") #'2015-05-28T09:00:00-07:00'
    # print(start_string, type(start_string))
    start_string = start_string + tz_string
    # print(start_string, type(start_string))
    end_string = datetime.datetime.fromtimestamp(end_int).strftime('%Y-%m-%dT%H:%M:%S')
    end_string = end_string + tz_string
    start_summary_string = datetime.datetime.fromtimestamp(start_int).strftime("%#I:%M%p") # I think the \# removes the leading zero on the hour!
    # print(start_summary_string)


    # print('start_string=', start_string)
    # print('end_string=', end_string)

    # https://developers.google.com/calendar/v3/reference/events/insert
    EVENT = {
        'summary': '{0} to {1}'.format(travelTypeString, destination),
        'start':   {'dateTime': start_string},  # needs to be a datetime string like '2015-05-28T09:00:00-07:00'
        'end':     {'dateTime': end_string},
        'location': destination,
    }

    e = service.events().insert(calendarId='8fi3dd5r0n9u5dsap2bnpkcd2o@group.calendar.google.com',
            sendNotifications=True, body=EVENT).execute()



def writeShow(venue, show_start_int, show_end_int, tz_string, warmup_start_int, show_duration):

    venue = venue
    show_duration = show_duration/60
    # turns an int into a string
    start_string = datetime.datetime.fromtimestamp(show_start_int).strftime("%Y-%m-%dT%H:%M:%S") #'2015-05-28T09:00:00-07:00'
    # print(start_string, type(start_string))
    start_string = start_string + tz_string
    # print(start_string, type(start_string))
    end_string = datetime.datetime.fromtimestamp(show_end_int).strftime('%Y-%m-%dT%H:%M:%S')
    end_string = end_string + tz_string
    start_summary_string = datetime.datetime.fromtimestamp(show_start_int).strftime("%#I:%M%p") # I think the \# removes the leading zero on the hour!
    # print(start_summary_string)


    # print('start=', start)
    # print('end=', end)

    # https://developers.google.com/calendar/v3/reference/events/insert
    EVENT = {
        'summary': 'Show at {0} for {1} minutes'.format(venue, show_duration),
        'start':   {'dateTime': start_string},  # needs to be a datetime string like '2015-05-28T09:00:00-07:00'
        'end':     {'dateTime': end_string},
        'location': venue,
        'colorId': '1'
    }

    e = service.events().insert(calendarId='8fi3dd5r0n9u5dsap2bnpkcd2o@group.calendar.google.com',
            sendNotifications=True, body=EVENT).execute()

# WRITE THE WARMUP TOO
