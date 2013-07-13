"""
Export nikeplus data to csv or print to screen
"""

import argparse
from collections import namedtuple
import csv
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


def _parse_args():
    """Parse sys.argv arguments"""

    token_file = os.path.expanduser('~/.nikeplus_access_token')

    parser = argparse.ArgumentParser(description='Export NikePlus data to CSV')

    parser.add_argument('-t', '--token', required=False, default=None,
                        help=('Access token for API, can also store in file %s'
                        ' to avoid passing via command line' % (token_file)))

    args = vars(parser.parse_args())

    if args['token'] is None:
        try:
            with open(token_file, 'r') as _file:
                    access_token = _file.read()
        except IOError:
            print 'Must pass access token via command line or store in file %s' % (
                                                                    token_file)
            sys.exit(-1)

        args['token'] = access_token

    return args



def calculate_mile_pace(duration, miles):
    pace = ''
    sp = duration.split(':')
    if (len(sp) == 3):
        duration_seconds = int(sp[0]) * 60 * 60 + int(sp[1]) * 60 + int(sp[2])
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


def get_activities(access_token):
    base_url = 'https://api.nike.com'

    url = '/me/sport/activities?access_token=%s' % access_token

    # weird required headers, blah.
    headers = {'appid':'fuelband', 'Accept':'application/json'}
    current_month = None

    while url:
        req = urllib2.Request('%s%s' % (base_url, url), None, headers)
        r = urllib2.urlopen(req)
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
    activities = get_activities(args['token'])

    # Print header
    activity = activities.next()
    print ','.join(activity._fields)

    writer = csv.writer(sys.stdout)
    for activity in activities:
        activity = activity._asdict()
        values = [str(value) for value in activity.values()]

        writer.writerow(values)


if __name__ == '__main__':
    main()
