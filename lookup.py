import googlemaps # https://googlemaps.github.io/google-maps-services-python/docs/
from datetime import datetime
# import re
import sys
sys.path.insert(0, 'C:\Dropbox (RC)\Apps')
import time
import json
import gspread
from httplib2 import Http
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import file, client, tools


"""
This is using google directions api, not google distance matrix

Flying like a beautiful bird
I'm high as a kite
Don't you think I know what I'm worth?
Why I gotta come down to earth?
When I'm high

"""

gmaps = googlemaps.Client(key='             ')

now = datetime.now()

def lookup(mode, origin, destination, timeVariable, trafficModel):#, arrival_time, departure_time):

    if mode == 'depart at':
        try:
            directions_result = gmaps.directions(
                                                origin,
                                                destination,
                                                departure_time = timeVariable,
                                                traffic_model = trafficModel,
                                            )
            duration = (directions_result[0]['legs'][0]["duration_in_traffic"]["value"]) * 1.1 # added 10% buffer on top of google's best_guess for cars

        except:
            duration = 'unknown'
    if mode == 'arrive by':
        # this is a little trickier
        try:

            # first we have to look up how long it would take if there wasn't traffic because that's all google's arrival_time parameter allows us to do.
            no_traffic_result = gmaps.directions(
                                                origin,
                                                destination,
                                                arrival_time = timeVariable
                                            )
            no_traffic_duration = (no_traffic_result[0]['legs'][0]['duration']['value']) # used to text

            # now that we know how long it takes to arrive at a certain time without traffic,
            traffic_result = gmaps.directions(
                                                origin,
                                                destination,
                                                departure_time = timeVariable - (no_traffic_duration * 1.3),
                                                traffic_model = trafficModel,
                                            )
            duration = (traffic_result[0]['legs'][0]['duration_in_traffic']['value']) * 1.1 # added 10% buffer on top of google's best_guess for cars
            print(mode, origin, destination, duration/60)

        except:
            duration = 'unknown'

    return duration
