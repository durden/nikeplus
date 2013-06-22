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

NikePlusActivity = namedtuple('NikePlusActivity',
                              ['start_time', 'miles', 'duration', 'pace'])


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
    # 2013-05-26T14:48:42Z
    start_time = time.strptime(activity.get('startTime'), '%Y-%m-%dT%H:%M:%SZ')

    metrics = activity.get('metricSummary')
    miles = km_to_mi(metrics.get('distance'))

    # remove milliseconds
    duration = metrics.get('duration').partition('.')[0]

    pace = calculate_mile_pace(duration, miles)
    activity = NikePlusActivity(start_time, miles, duration, pace)

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

            distance = '%.2f' % round(activity.miles, 2)
            date = time.strftime('%a %m/%d/%y', activity.start_time)
            month = time.strftime('%B', activity.start_time)

            if month != current_month:
                current_month = month
                print ''
                print '--', current_month, '--'

            print '%s : %s miles %s %s' % (date, distance, activity.duration,
                                           activity.pace)

        # pagination
        url = None
        if resp.get('paging') and resp.get('paging').get('next'):
            url = resp.get('paging').get('next')


if __name__ == '__main__':
    main()
