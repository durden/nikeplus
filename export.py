""" Nike plus activity log
https://developer.nike.com

Output:
-- May --
Sun 05/26/13 : 5000 points 5.59 miles 1:02:20 (11'10/mi)
Fri 05/24/13 : 2000 points 4.01 miles 0:37:40 (9'24/mi)
Wed 05/22/13 : 3000 points 6.17 miles 1:01:12 (9'55/mi)
"""


from collections import namedtuple
import json
import urllib
import urllib2
import time

# Insert token here
ACCESS_TOKEN = ''

# FIXME: Could use descriptors here:
#   - Could hold: default value, api name, pretty name, and conversion func

# Key = our internal name
# Value = nike plus API name (None for custom, not represented in API)
name_to_api = {'calories': 'calories',
               'fuel': 'fuel',
               'distance': 'distance',
               'steps': 'steps',
               'start_time': 'startTime',
               'device': 'deviceType',
               'miles': None,
               'duration': 'duration',
               'pace': None}

NikePlusActivity = namedtuple('NikePlusActivity', name_to_api.keys())

km_to_mi = lambda distance: distance * 0.621371


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

    # 2013-05-26T14:48:42Z
    api_values['start_time'] = time.strptime(api_values['start_time'],
                                            '%Y-%m-%dT%H:%M:%SZ')
    api_values['start_time'] = time.strftime('%a %m/%d/%y',
                                             api_values['start_time'])

    # remove milliseconds
    api_values['duration'] = api_values['duration'].partition('.')[0]

    api_values['miles'] = km_to_mi(api_values['distance'])
    api_values['distance'] = '%.2f' % round(api_values['miles'], 2)
    api_values['pace'] = calculate_mile_pace(api_values['duration'],
                                             api_values['miles'])

    activity = NikePlusActivity(**api_values)

    return activity


def main():
    base_url = 'https://api.nike.com'
    url = '/me/sport/activities?access_token=%s' % ACCESS_TOKEN
    headers = {'appid':'fuelband', 'Accept':'application/json'} # weird required headers, blah.
    current_month = None

    while url:
        req = urllib2.Request('%s%s' % (base_url, url), None, headers)
        r = urllib2.urlopen(req)
        resp = json.loads(r.read())
        r.close()

        data = resp.get('data')
        if data is None:
            return

        for item in resp.get('data'):
            activity = decode_activity(item)
            print activity

        # pagination
        url = None
        if resp.get('paging') and resp.get('paging').get('next'):
            url = resp.get('paging').get('next')


if __name__ == '__main__':
    main()
