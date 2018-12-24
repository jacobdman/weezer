from __future__ import print_function #delete?
import apiclient
from apiclient.discovery import build
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import file, client, tools
import googlemaps # https://googlemaps.github.io/google-maps-services-python/docs/
import gspread
from httplib2 import Http #delete?
import json
from lookup import lookup
import datetime
import pytz
import requests
import schedule
import time
import timezonefinder
from timezonefinder import * #delete
from timezonefinder import TimezoneFinder
from tzLookup import *
from writeAppointments import *
from datetime import datetime
from pprint import pprint#delete
import sys
import os
from convert import *


"""
This program pulls appointments from a spreadsheet and puts them into a google calendar, along with drive times.

view the sample spreadsheet here:
https://docs.google.com/spreadsheets/d/1HwiCcFR0Ti73PazEys5Ae0aVP4dPuRUvyjlOh8hZb68/edit#gid=2070232885

view the sample google calendar here:
https://calendar.google.com/calendar?cid=OGZpM2RkNXIwbjl1NWRzYXAyYm5wa2NkMm9AZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ
"""


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# use credentials to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
credentials = ServiceAccountCredentials.from_json_keyfile_name(resource_path('drivetimes-f9856c45d8c0.json'), scope)

# gspread old drive delete
client = gspread.authorize(credentials)
sheet = client.open("Weezer Spring Tour 2019").sheet1
codeSheet = client.open("Weezer Spring Tour 2019").worksheet('codes')

# Extract all of the values
driveList = sheet.get_all_records()

# Leave a five star review and i'll leave you one too


"""
DELETE BLANK ROWS
"""
print('Deleting blank rows from the sheet...')
rowIndex = 2 # google sheets are not zero indexed and you want to skip the header row when you deleete
for rowDictionary in driveList:

    if rowDictionary['date'] == '':

        sheet.delete_row(rowIndex)
    else:
        rowIndex = rowIndex + 1

# Extract all of the values again
driveList = sheet.get_all_records()

"""
DELETE OLD DRIVES
"""
print('Deleting old drives...')

rowIndex = 2 # google sheets are not zero indexed and you want to skip the header row when you delete

# iterate through the list of dicts
for row in driveList:  # gspread doesn't include the HEADER!!!

    if not row['date'] == '':

        destination = row['destination']

        year = str(row['year'])
        readable_date_string = row['date']
        timeVariable = row['timeVariable']

        timeVariableStamp = convert_readable_date_to_timestamp(year, readable_date_string, timeVariable)

        driveDate_int = convertStringsToEpoch(timeVariableStamp)

        if driveDate_int < time.time():

            sheet.delete_row(rowIndex)

            print(f'(Drive to {destination} on {readable_date_string} deleted)')

        else:
            rowIndex = rowIndex + 1

# sys.exit()

"""
LOOK UP NEW DRIVES
"""
# Extract all of the values again
driveList = sheet.get_all_records()

rowIndex = 2

# get the code bank as a dictionary from the code sheet
codeList = codeSheet.col_values(1)
addressList = codeSheet.col_values(2)
codeDict = dict(zip(codeList, addressList))

print('Looking up new drive times...')
for row in driveList:

    if not row['origin'] == '':

        # Get the Variables
        driveDate = row['date']
        timeVariable = row['timeVariable'].replace(' ', '')
        show_start = row['show_start']
        year = str(row['year'])
        joined_time_string = year + driveDate + ' ' + timeVariable
        dt = datetime.datetime.strptime(joined_time_string, "%Y%A, %B %d %I:%M%p")
        timeVariableStamp = dt.strftime("%Y-%m-%dT%H:%M:%S")
        if driveDate == '':
            continue
        travel_type = 'drive'
        origin = row['origin'].strip()#.replace('home', home)
        destination = row['destination'].strip()
        if not destination:
            continue
        mode = row['mode'].strip()
        event_duration = row['event_duration']

        # check for there_and_back travel_type. The app will schedule a return drive at the end of the appointment.
        if not event_duration == '':  # if there is an appointment

            if show_start == '':    # if the appointment is not a show

                travel_type = 'there_and_back'

        # for flights, check for flight mode:
        flightDurationString = row['flightDuration']  # expecting 1:00 [ 1:00:00 AM ]

        # accomodate different data types in the google sheet
        if not flightDurationString == '':

            if type(flightDurationString) == int:

                flightSecondsInt = flightDurationString * 60

            else:

                # remove milliseconds and seconds from flight duration strings
                if len(flightDurationString) > 5:

                    flightDurationString = flightDurationString[:-3]

                flightSecondsInt = get_sec(flightDurationString)

            travel_type = 'flight'

        # get more variables for flight mode
        origin1 = row['origin']
        origin2 = row['destinationAirport']
        destination1 = row['originAirport']
        destination2 = row['destination']
        originAirport = row['originAirport']

        # check for slower conditions, such as 'rain' or 'bus' that would necessitate a more pessimistic time in traffic duration from google.
        if row['notes']:

            trafficModel = 'pessimistic'

        else:

            trafficModel = 'best_guess'

        """
        i wonder what it’s like out there
        And my eyes are two far away spaceships
        you are a sealed up door
        Yeah, there's gotta be more to our lives than this
        """



        # replace the address codes with the actual addresses
        if destination in codeDict:
            destination = codeDict[destination]
        if origin1 in codeDict:
            origin1 = codeDict[origin1]
        if destination1 in codeDict:
            destination1 = codeDict[destination1]
        if destination2 in codeDict:
            destination2 = codeDict[destination2]
        if origin2 in codeDict:
            origin2 = codeDict[origin2]
        if origin in codeDict:
            origin = codeDict[origin]
        if originAirport in codeDict:
            originAirport = codeDict[originAirport]

        # add 'airport' to 3 letter airport coaes, such as 'OAK', so google can find it
        if len(origin2.strip()) == 3:
            origin2 = origin2 + ' airport'
        if len(originAirport.strip()) == 3:
            originAirport = originAirport + ' airport'

        # for flights:
        if travel_type == 'flight':
            # print('analyzing a flight row')

            if mode == 'arrive by':

                # Calculate the second drive first, as that determines the times for the first drive
                # lookup timezone
                coordinates2 = get_coordinates(destination2)
                tz = tzLookup(coordinates2, dt)    # -06:00 # this is that weird service that needs a time string
                arrive_by2String = timeVariableStamp #+ tz  # 2018-7-30T10:0:00-06:00
                try:
                    arrive_by2Int = convertStringsToEpoch(arrive_by2String)
                except:
                    print('failed to convert Time string to Epoch time')
                # print('fly to', origin2, 'then drive to', destination2, 'arriving by', arrive_by2Int)
                drive2googleTime = int(lookup(mode, origin2, destination2, arrive_by2Int, trafficModel)/60)


                # convert the googletime to safeTime
                safeTime2 = int(convert(drive2googleTime))

            if mode == 'depart at':

                # calculate the first drive first
                # lookup timezone
                coordinates = get_coordinates(origin)
                tz = tzLookup(coordinates, dt)
                depart_at1String = timeVariableStamp #+ tz
                try:
                    depart_at1Int = convertStringsToEpoch(depart_at1String)
                    # print('epoch time =', depart_at1Int)
                except:
                    print('failed to convert Time string to Epoch time')

                drive1googleTime = int(lookup(mode, origin1, destination1, depart_at1Int, trafficModel)/60)#, arrival_time, departure_time) # you want to add a parameter here to lookup

                # convert the googletime to safeTime
                safeTime1 = int(convert(drive1googleTime))

            # print drives and flight for arrive by mode to calendar
            if mode == 'arrive by':

                depart_by2ForCalendarInt = arrive_by2Int - safeTime2*60
                # print drive 2 to calendar
                writeDrive(destination2, depart_by2ForCalendarInt, arrive_by2Int, tz, 'Drive ')
                # calculate the flight
                flightEnd = depart_by2ForCalendarInt - 600 # seconds = 10 minutes

                flightStart = flightEnd - flightSecondsInt

                # print the flight
                writeDrive(origin2, flightStart, flightEnd, tz, 'Fly ')

                # calculate the first drive
                arrive_by1Int = flightStart - 600 # 10 minutes = 600 seconds
                drive1googleTime = int(lookup(mode, origin1, destination1, arrive_by1Int, trafficModel)/60)
                safeTime1 = int(convert(drive1googleTime))

                depart_by1ForCalendarInt = arrive_by1Int - safeTime1*60  # in seconds?

                # print drive 1
                writeDrive(destination1, depart_by1ForCalendarInt, arrive_by1Int, tz, 'Drive ')

            # print drives and flight for depart at mode to calendar
            if mode == 'depart at':
                # print drive 1
                arrive_by1ForCalendarInt = safeTime1*60 + depart_at1Int
                writeDrive(destination1, depart_at1Int, arrive_by1ForCalendarInt, tz, 'Drive')

                flightStart = arrive_by1ForCalendarInt + 600 # seconds = 10 minutes?
                # print(flightStart)
                flightEnd = flightStart + flightSecondsInt
                # print()
                writeDrive(origin2, flightStart, flightEnd, tz, 'Fly')
                depart_by2Int = flightEnd + 600 # seconds? 10 minutes
                drive2googleTime = int(lookup(mode, origin2, destination2, depart_by2Int, trafficModel)/60)
                safeTime2 = int(convert(drive2googleTime))
                arrive_by2ForCalendarInt = depart_by2Int + safeTime2*60  # in seconds?

                writeDrive(destination2, depart_by2Int, arrive_by2ForCalendarInt, tz, 'Drive')
                print(destination2, depart_by2Int, arrive_by2ForCalendarInt, tz, 'Drive')



        if travel_type == 'there_and_back':

            """
            I want Neil Young on your phone speaker in the morning
            And fuck him if he just can't see
            this is how his songs are supposed to be heard
            No more lectures on fidelity
            """

            if mode == 'arrive by':

                coordinates1 = get_coordinates(destination)

                tz1 = tzLookup(coordinates1, dt)    # -06:00 # this is that weird service that needs a time string

                arrive_by1 = timeVariableStamp# + tz1  # 2018-7-30T10:0:00-06:00

                try:
                    arrive_by1 = convertStringsToEpoch(arrive_by1)#
                    # print('arrive_by1 epoch time =', arrive_by1)
                except:
                    print('failed to convert Time string to Epoch time')
                print('mode, origin, destination, arrive_by =', mode, origin, destination, arrive_by1, trafficModel)
                googleTime1 = int(lookup(mode, origin, destination, arrive_by1, trafficModel)/60)
                coordinates2 = get_coordinates(origin)

                tz2 = tzLookup(coordinates2, dt)    # -06:00 # this is that weird service that needs a time string

                depart_at2 = timeVariableStamp# + tz2#+ tz  # 2018-7-30T10:0:00-06:00

                try:
                    depart_at2 = convertStringsToEpoch(depart_at2) + mins_to_secs(event_duration)

                except:
                    print('failed to convert Time string to Epoch time')
                googleTime2 = int(lookup(mode, origin, destination, depart_at2, trafficModel)/60)

            if mode == 'depart at':
                print('haven\'t coded this yet. use arrive_by mode')
                """
                Because life will make a beggar of rich men
                Bring a sovereign to his knee--hee--hees
                And all the gold and all of the platinum
                Melting like a drop in the seas
                The only way
                To escape
                Is to dance, dance in the flames
                """



            safeTime1 = int(convert(googleTime1))


            safeTime2 = int(convert(googleTime2))


            # print to calendar
            if mode == 'arrive by':
                depart_byForCalendar1 = arrive_by1 - safeTime1*60

                arrive_by2ForCalendar = depart_at2 + safeTime2*60

                writeDrive(destination, depart_byForCalendar1, arrive_by1, tz1, 'Drive ')

                writeDrive(origin, depart_at2, arrive_by2ForCalendar, tz2, 'Drive ')

            if mode == 'depart at':
                print('haven\'t coded this yet. use arrive_by mode')
                # sys.exit(0)

        # for one way, one-stop rides:
        if travel_type == 'drive':

            if mode == 'arrive by':
                # lookup timezone
                coordinates = get_coordinates(destination)

                tz = tzLookup(coordinates, dt)    # -06:00 # this is that weird service that needs a time string
                arrive_by = timeVariableStamp #+ tz  # 2018-7-30T10:0:00-06:00
                try:
                    arrive_by = convertStringsToEpoch(arrive_by)
                except:
                    print('failed to convert Time string to Epoch time')
                googleTime = int(lookup(mode, origin, destination, arrive_by, trafficModel)/60)
            if mode == 'depart at':
                # lookup timezone
                coordinates = get_coordinates(origin)
                # print('coordinates', coordinates)
                tz = tzLookup(coordinates, dt)
                # print(tz)
                depart_at = timeVariableStamp #+ tz
                try:
                    depart_at = convertStringsToEpoch(depart_at)
                except:
                    print('failed to convert Time string to Epoch time')
                print(mode, origin, destination, depart_at, trafficModel)
                googleTime = int(lookup(mode, origin, destination, depart_at, trafficModel)/60)#, arrival_time, departure_time) # you want to add a parameter here to lookup

            safeTime = int(convert(googleTime))
            print('safeTime =',safeTime)

            # print to calendar
            if mode == 'arrive by':

                """

                Tried to get my thoughts on paper
                Comb my hair like I'm a gangster
                Gotta do the dog and pony show
                Algorithms sure ain't helping
                Prefrontal cortex is melting
                I'm  goin' where the weather suits my clothes
                """

                depart_byForCalendar = arrive_by - safeTime*60
                # print the drive
                writeDrive(destination, depart_byForCalendar, arrive_by, tz, 'Drive ')

            if mode == 'depart at':

                arrive_byForCalendar = safeTime*60 + depart_at

                writeDrive(destination, depart_at, arrive_byForCalendar, tz, 'Drive ')


# for shows:
    show_start = row['show_start']

    if not show_start == '':
        try:
            coordinates = get_coordinates(destination)
        except:
            print('is your destination missing?')
        # print(coordinates)
        tz = tzLookup(coordinates, dt)
        event_duration_secs = mins_to_secs(event_duration)#(row['event_duration'])
        show_start_string = convert_readable_date_to_timestamp(year, driveDate, show_start)
        show_start_int = convertStringsToEpoch(show_start_string)
        # event_duration_seconds_int = convertMinsToSecs(event_duration_string)
        show_end_int = show_start_int + event_duration_secs

        writeShow(destination, show_start_int, show_end_int, tz, timeVariableStamp, event_duration_secs)

    rowIndex = rowIndex + 1


print('printing the date last updated')
now = datetime.datetime.now()
now = now.strftime('%A, %#I:%M %p') # the \# removes the leading zero on the hour
string = 'Last updated {0}'.format(now)

updateList = ['', string] # DON'T USE THE FIRST COLUMN

sheet.append_row(updateList)
