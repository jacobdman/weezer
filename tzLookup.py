from timezonefinder import TimezoneFinder
import requests
import json
import datetime
from convert import *
import googlemaps
import pprint
import time
import pytz
from datetime import datetime, timedelta
from time import sleep

# check to see if we're currently in daylight savings time
def is_dst():

    dst = time.localtime().tm_isdst
    # print('dst', dst)
    return dst

# check to see if a date is in daylight savings time
def is_future_dst(zonename, dt):
    tz = pytz.timezone(zonename)
    d = pytz.utc.localize(dt)
    return d.astimezone(tz).dst() != timedelta(0)

def get_coordinates(destination):

    API_key = '[INSERT YOUR KEY]'

    gm = googlemaps.Client(key = API_key)
    # print(gm)
    try:
        geocode_result = gm.geocode(destination)[0]
    except:
        print('GOOGLES GEOCODE API is not working. Upgrade? https://developers.google.com/maps/documentation/geocoding/intro')
    lat = str(geocode_result['geometry']['location']['lat'])
    long = str(geocode_result['geometry']['location']['lng'])
    coordinates = lat + ',' + long

    return coordinates

def tzLookup(coordinates, dt):
    Account_id = '[INSERT YOUR ID]'
    API_key	= '[INSERT YOUR KEY]'
    destination = coordinates

    url = 'https://api.askgeo.com/v1/ Account_id     /API_key /query.json?databases=TimeZone&points={}'.format(destination)

    response = requests.get(url)

    jDict = json.loads(response.content)

    jList = jDict['data']

    subDict = (jList[0])

    subsubDict = (subDict['TimeZone'])

    tz = (subsubDict['CurrentOffsetMs'])

    dst = subsubDict['InDstNow']

    TimeZoneId = subsubDict['TimeZoneId']

    future_dst = is_future_dst(TimeZoneId, dt)

    # we're adjusting the tz by an hour if there's a daylight savings time differential. we've chosen this spot in the code because the times are ints. it's kind of arbitrary
    if is_dst():

        if not future_dst:

            print('we\'re in daylight savings time now but the future appointment is not.')
            # print('old tz =', millisToString(tz))
            tz = tz - (3600 * 1000) #seconds an hour
            # print('new tz =', millisToString(tz))
    if not is_dst():

        if future_dst:

            print('we\'re not in daylight savings time now but the future appointment is.')
            # print('old tz =', millisToString(tz))
            tz = tz + (3600 * 1000) #seconds an hour
            # print('new tz =', millisToString(tz))
    # print(tz)
    tz = millisToString(tz)
    # print('tz = ', tz)
    return tz

"""
She was into me
Then she changed the dial like i'm grunge or gangsta rap
Now I'm hanging out
With a kitty cat named Baudelaire on my lap
I never stopped her planets turning, noooooo!

hey man cheer up
Make your own luck
Have a nice life
have some more Sprite

"""