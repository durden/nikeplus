#! /usr/bin/env python

"""
Export nikeplus data to csv or print to screen
"""

import argparse
from collections import namedtuple
import csv
from datetime import datetime
import json
import os.path
import sys
import time
import urllib2

# FIXME: Could use descriptors here:
#   - Could hold: default value, api name, pretty name, and conversion func

# Key = our internal name
# Value = nike plus API name (None for custom, not represented in API)
name_to_api = {'calories': 'calories',
               'fuel': 'fuel',
               'steps': 'steps',
               'device': 'deviceType',
               'duration': 'duration',
               'pace': None,
               'kilometers': None,
               'miles': None,

               # Time in iso format as string
               'start_time': 'startTime',

               # Redundant now but easier to include since it maps directly to
               # the API.
               'distance': 'distance'}

NikePlusActivity = namedtuple('NikePlusActivity', name_to_api.keys())

km_to_mi = lambda distance: distance * 0.621371

DATE_FMT = '%Y-%m-%d'


def _validate_date_str(str_):
    """Validate str as a date and return string version of date"""

    if not str_:
        return None

    # Convert to datetime so we can validate it's a real date that exists then
    # convert it back to the string.
    try:
        date = datetime.strptime(str_, DATE_FMT)
    except ValueError:
        msg = 'Invalid date format, should be YYYY-MM-DD'
        raise argparse.ArgumentTypeError(msg)

    return date.strftime(DATE_FMT)


def _parse_args():
    """Parse sys.argv arguments"""

    token_file = os.path.expanduser('~/.nikeplus_access_token')

    parser = argparse.ArgumentParser(description='Export NikePlus data to CSV')

    parser.add_argument('-t', '--token', required=False, default=None,
                        help=('Access token for API, can also store in file %s'
                        ' to avoid passing via command line' % (token_file)))
    parser.add_argument('-s', '--since', type=_validate_date_str,
                        help=('Only process entries starting with YYYY-MM-DD '
                              'and newer'))

    args = vars(parser.parse_args())

    if args['token'] is None:
        try:
            with open(token_file, 'r') as _file:
                access_token = _file.read().strip()
        except IOError:
            print 'Must pass access token via command line or store in file %s' % (
                                                                    token_file)
            sys.exit(-1)

        args['token'] = access_token

    return args



def calculate_mile_pace(duration, miles):
    pace = ''
    sp = duration.split(':')
    if len(sp) == 3:
        duration_seconds = int(sp[0]) * 60 * 60 + int(sp[1]) * 60 + int(sp[2])

        seconds_per_mile = 0.0
        if miles:
            seconds_per_mile = duration_seconds / miles

        hours, remainder = divmod(seconds_per_mile, 3600)
        minutes, seconds = divmod(remainder, 60)
        pace = '(%.0f\'%02.0f/mi)' % (minutes, seconds)

    return pace


def decode_activity(activity):
    metrics = activity.get('metricSummary')

    api_values = {}
    for pretty_name, api_name in name_to_api.iteritems():
        if api_name is not None:
            # Values can be in 1 of 2 dicts, metric sub-dict or 'root' activity
            # dict
            try:
                api_values[pretty_name] = metrics[api_name]
            except KeyError:
                api_values[pretty_name] = activity.get(api_name, None)

    # Custom values/sanitizing

    # remove milliseconds
    api_values['duration'] = api_values['duration'].partition('.')[0]

    # Distance will be redundant to kilometers, but leaving both b/c it's
    # easier b/c the name_to_api dict is used to pull data from API, map to
    # named tuple dynamically, etc.  It's just a pain to remove it from here
    # and still have a dynamic dict from named tuple, would have to manually
    # remove it in a few places which feels hack-ish.
    api_values['miles'] = km_to_mi(api_values['distance'])
    api_values['kilometers'] = api_values['distance']

    api_values['pace'] = calculate_mile_pace(api_values['duration'],
                                             api_values['miles'])

    activity = NikePlusActivity(**api_values)

    return activity


def get_activities(access_token, start_date=None):
    base_url = 'https://api.nike.com'

    url = '/me/sport/activities?access_token=%s' % access_token

    if start_date is not None:
        # FIXME: use re module to assert that it's yyyy-mm-dd
        end_date = datetime.today().strftime(DATE_FMT)
        url = '%s&startDate=%s&endDate=%s' % (url, start_date, end_date)

    # weird required headers, blah.
    headers = {'appid':'fuelband', 'Accept':'application/json'}
    current_month = None

    while url:
        req = urllib2.Request('%s%s' % (base_url, url), None, headers)

        try:
            r = urllib2.urlopen(req)
        except urllib2.HTTPError as err:
            print 'Failed sending request to "%s":\n%s\n%s\n\n' % (url, err,
                                                                   err.read())
            raise err

        resp = json.loads(r.read())
        r.close()

        data = resp.get('data')
        if data is None:
            raise StopIteration

        for item in resp.get('data'):
            activity = decode_activity(item)
            yield activity

        # pagination
        url = None
        if resp.get('paging') and resp.get('paging').get('next'):
            url = resp.get('paging').get('next')


def main():
    args = _parse_args()
    activities = get_activities(args['token'], args['since'])

    # Print header
    activity = activities.next()
    print ','.join(activity._fields)

    # FIXME: Bug in nikeplus API, if you send request with start/end you'll
    # get in an infinite loop telling a new offset for data that doesn't
    # exist. For example:
    #   Request data for 2013-08-15 - 2013-09-01
    #   Only have data for 2013-08-15 and 2013-08-16
    #   API keeps returning a new offset each time for 5 more days but
    #   it continues to return data for the same two days and never stops.
    #   See nikeplus_api_bug.txt for detailed output of this scenario.
    seen_dates = set()

    writer = csv.writer(sys.stdout)
    for activity in activities:
        activity = activity._asdict()
        values = [str(value) for value in activity.values()]

        # Already seen this date, API is returning duplicate data so must mean
        # we've been through it all.
        if activity['start_time'] in seen_dates:
            break

        seen_dates.add(activity['start_time'])

        writer.writerow(values)


if __name__ == '__main__':
    main()
