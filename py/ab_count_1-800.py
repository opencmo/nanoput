from __future__ import print_function
from redis import StrictRedis
from datetime import datetime
from dateutil import tz

r = StrictRedis(host='segments.opendsp.com', port=6379, db=0)

campaigns = sorted({'295'})

tss = sorted({'1789', '1790', '1791', '1792', '1793', '1794', '1795', '1796', '1797', '1798'})

segments = sorted({'archived:segment:134:fp:180', 'archived:segment:137:fp:180', 'archived:segment:138:fp:180',
                   'archived:segment:139:fp:180', 'archived:segment:140:fp:180'})

separations = ['T', 'C']


def render(type_var, type_id):
    for separation in separations:
        experiment = 'ab_test2_{}_{}_{}'.format(type_var, type_id, separation)
        print('{} assignments: {}'.format(separation, r.zcard(experiment)))

    for segment in segments:
        print('\nSegment: {}'.format(segment[17:]))
        for separation in separations:
            zkey = 'ab_test2_{}_int_{}_{}_{}'.format(segment, type_var, type_id, separation)
            experiment = 'ab_test2_{}_{}_{}'.format(type_var, type_id, separation)
            print('{} intersection: {}'.format(separation, r.zinterstore(zkey, [segment, experiment])))
            r.delete(zkey)


now = datetime.utcnow().replace(tzinfo=tz.tzutc())
date = now.strftime('%Y-%m-%d %H:%M %Z')

print('Segments stats ({}):\n'.format(date))
for segment in segments:
    print('Segment {} total count: {}'.format(segment[17:], r.zcard(segment)))

for campaign in campaigns:
    print('\n' * 3, 'Campaign: {}'.format(campaign), sep='')
    render('c', campaign)

for ts in tss:
    print('\n' * 3, 'TS: {}'.format(ts), sep='')
    render('ts', ts)
