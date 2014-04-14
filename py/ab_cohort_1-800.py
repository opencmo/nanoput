from __future__ import print_function
from redis import StrictRedis
from datetime import datetime
from dateutil import tz

r = StrictRedis(host='segments.opendsp.com', port=6379, db=0)

ts_1797_T = set(r.zrange('ab_test2_ts_1797_T', 0, -1))
ts_1797_C = set(r.zrange('ab_test2_ts_1797_C', 0, -1))

ts_1798_T = set(r.zrange('ab_test2_ts_1798_T', 0, -1))
ts_1798_C = set(r.zrange('ab_test2_ts_1798_C', 0, -1))

ts_1797_union = ts_1797_T | ts_1797_C
ts_1798_union = ts_1798_T | ts_1798_C

# https://baatoot.atlassian.net/browse/OPS-2729
ts_1797_T_only = ts_1797_T - ts_1798_union  # 1
ts_1797_C_only = ts_1797_C - ts_1798_union  # 2

ts_1798_T_only = ts_1798_T - ts_1797_union  # 3
ts_1798_C_only = ts_1798_C - ts_1797_union  # 4

ts_1797_T_int_ts_1798_T = ts_1797_T & ts_1798_T  # 5
ts_1797_C_int_ts_1798_T = ts_1797_C & ts_1798_T  # 6
ts_1797_T_int_ts_1798_C = ts_1797_T & ts_1798_C  # 7
ts_1797_C_int_ts_1798_C = ts_1797_C & ts_1798_C  # 8


now = datetime.utcnow().replace(tzinfo=tz.tzutc())
date = now.strftime('%Y-%m-%d %H:%M %Z')

print('A/B Overall Stats ({}):\n'.format(date))

print('1: 1797_T_without_1798 - {}'.format(len(ts_1797_T_only)))
print('2: 1797_C_without_1798 - {}'.format(len(ts_1797_C_only)))

print('3: 1798_T_without_1797 - {}'.format(len(ts_1798_T_only)))
print('4: 1798_C_without_1797 - {}'.format(len(ts_1798_C_only)))

print('5: 1797_T_intersect_1798_T - {}'.format(len(ts_1797_T_int_ts_1798_T)))
print('6: 1797_C_intersect_1798_T - {}'.format(len(ts_1797_C_int_ts_1798_T)))

print('7: 1797_T_intersect_1798_C - {}'.format(len(ts_1797_T_int_ts_1798_C)))
print('8: 1797_C_intersect_1798_C - {}'.format(len(ts_1797_C_int_ts_1798_C)))


segments = sorted({
    'archived:segment:134:fp:180',
    'archived:segment:137:fp:180',
    'archived:segment:138:fp:180',
    'archived:segment:139:fp:180',
    'archived:segment:140:fp:180'
})

for segment in segments:
    users = set(r.zrange(segment, 0, -1))
    print('\nSegment {}:\n'.format(segment[17:]))

    print('1: 1797_T_without_1798 - {}'.format(len(users & ts_1797_T_only)))
    print('2: 1797_C_without_1798 - {}'.format(len(users & ts_1797_C_only)))

    print('3: 1798_T_without_1798 - {}'.format(len(users & ts_1798_T_only)))
    print('4: 1798_C_without_1798 - {}'.format(len(users & ts_1798_C_only)))

    print('5: 1797_T_intersect_1798_T - {}'.format(len(users & ts_1797_T_int_ts_1798_T)))
    print('6: 1797_C_intersect_1798_T - {}'.format(len(users & ts_1797_C_int_ts_1798_T)))

    print('7: 1797_T_intersect_1798_C - {}'.format(len(users & ts_1797_T_int_ts_1798_C)))
    print('8: 1797_C_intersect_1798_C - {}'.format(len(users & ts_1797_C_int_ts_1798_C)))
