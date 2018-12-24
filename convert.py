import math
import time
import calendar
import datetime
import sys


def timestampToDateObject(timestamp):
    try:
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    except:
        try:
            dt = datetime.datetime.striptime(timestamp, "%Y-%m-%dT%H:%M:%S")
        except:
            pass
    print(dt)
    return dt

def timestamp_TZ_ToDateObject(timestamp):
	return datetime.datetime.strptime(timestamp[:-6], "%Y-%m-%dT%H:%M:%S")


def convert_readable_date_to_timestamp(year, readable_date_string, time_string):

    joined_time_string = year + readable_date_string + ' ' + time_string
    print(joined_time_string)

    try:
        timestamp = datetime.datetime.strptime(joined_time_string, "%Y%A, %B %d %I:%M%p")
    except:
        try:
            timestamp = datetime.datetime.strptime(joined_time_string, "%Y%A, %B %d %I:%M %p")
        except:
            try:
                timestamp = datetime.datetime.strptime(joined_time_string, "%Y%A, %B %d ")
            except:
                try:
                    timestamp = datetime.datetime.strptime(joined_time_string, "%Y%A, %B %d %I:%M:%S %p")
                except:

                    print('MISSING YEAR????')
                    sys.exit(0)

    timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%S")

    return timestamp

def convertStringsToEpoch(string):
    try:
        string = time.strptime(string, "%Y-%m-%dT%H:%M:%S")
    except:
        string = time.strptime(string, "%M:%S")
        print(string)

    epoch = int(time.mktime(string))

    return epoch

def get_min(time_str):
    try:
        h, m = time_str.split(':')
    except:
        h, m, s = time_str.split(':')
    return int(h) * int(3600/60) + int(m)

def get_sec(time_str):
    try:
        h, m = time_str.split(':')
    except:
        h, m, s = time_str.split(':')
    return (int(h) * int(3600/60) + int(m))*60

def roundup(x, base=5):
    return int(base * round(float(x)/base))

def minsToString(minutes):
    return '{:02d}:{:02d}'.format(*divmod(minutes, 60))

def mins_to_secs(minutes):
    return minutes*60

def millisToString(millis):
    millis=millis
    hours=(millis/(1000*60*60))
    # hours.rjust(5,'0')
    return ("%03d:00" % (hours))

def secs_to_days(seconds):
    return seconds/(60*60*24)

def xldate_to_datetime(xldate):
	temp = datetime(1900, 1, 1)
	delta = timedelta(days=xldate.days)
	return temp+delta

def convert(googleMinutes):

    late_departure = 15

    parking_nightmare = 5

    bufferMinutes = late_departure + parking_nightmare

    return (googleMinutes * 1.1) + bufferMinutes