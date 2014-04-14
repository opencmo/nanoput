#!/opt/enr/virtupy/bin/python
# $Id$
import operator
import gzip
import sys
import os
import subprocess
import struct
import time
import datetime
import calendar
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from common import *
import redis
from dateutil.parser import parse
import random

r = redis.StrictRedis(host='segments.opendsp.com', port=6379, db=0)        

camps = {
    '283':['1735','1736','1737','1754','1755','1756','1757','1758','1759'],
    '284':['1738','1739','1740','1760','1761','1762','1763','1764','1765'],
    '285':['1741','1742','1743','1766','1767','1768','1769','1770','1771'],
    '286':['1744','1745','1746','1772','1773','1774','1775','1776','1777']
}

to_camps = {
    '1735':'283','1736':'283','1737':'283','1754':'283','1755':'283','1756':'283','1757':'283','1758':'283','1759':'283',
    '1738':'284','1739':'284','1740':'284','1760':'284','1761':'284','1762':'284','1763':'284','1764':'284','1765':'284',
    '1741':'285','1742':'285','1743':'285','1766':'285','1767':'285','1768':'285','1769':'285','1770':'285','1771':'285',
    '1744':'286','1745':'286','1746':'286','1772':'286','1773':'286','1774':'286','1775':'286','1776':'286','1777':'286'
}

test_camps = dict()
control_camps = dict()
test_ts = dict()
control_ts = dict()
for c in camps:
    test_camps[c] = set()
    control_camps[c] = set()
    for ts in camps[c]:
        test_ts[ts] = set(r.zrange("ab_test2_ts_%s_T" % (ts), 0, -1))
        control_ts[ts] = set(r.zrange("ab_test2_ts_%s_C" % (ts), 0, -1))
        test_camps[c] = test_camps[c] | test_ts[ts]
        control_camps[c] = control_camps[c] | control_ts[ts]
    control_camps[c] = control_camps[c] - test_camps[c]
    
segments = dict()
for segment in ['archived:segment:362:fp:220', 'archived:segment:363:fp:220', 'archived:segment:364:fp:220', 'archived:segment:365:fp:220', 'archived:segment:366:fp:220']:
    segments[segment] = set(r.zrange(segment, 0, -1))    

f = open('/ebs3/boba/wins_moto.txt','r')
lines = f.readlines()
for line in lines:
    line = line.strip()
    line = line.split("\t")
    ts = line[0]
    user = line[2]
    control_camps[to_camps[ts]].discard(user)
    if user not in test_ts[ts]:
        test_camps[to_camps[ts]].discard(user)

for c in sorted(camps):
    print "For Campaign %s, Test: %s, Control: %s" % (c, len(test_camps[c]), len(control_camps[c]))
    for segment in sorted(segments):
        print "Intersection of T %s with %s: %s" % (c, segment, len(test_camps[c] & segments[segment]))
        print "Intersection of C %s with %s: %s" % (c, segment, len(control_camps[c] & segments[segment]))
    print "-------------------------------------------------------------------------"

print "RANDOMLY DIVEDED"

for c in sorted(camps):
    contr_size = len(control_camps[c]) / 2
    test_size = len(test_camps[c]) / 2
    contr1 = set(random.sample(control_camps[c], contr_size))
    contr2 = control_camps[c] - contr1
    test1 = set(random.sample(test_camps[c], test_size))
    test2 = test_camps[c] - test1
    print "For Campaign %s, Control1: %s, Control2: %s" % (c, len(contr1), len(contr2))
    print "For Campaign %s, Test1: %s, Test2: %s" % (c, len(test1), len(test2))
    for segment in sorted(segments):
        print "Intersection of Test1 with %s: %s" % (segment, len(test1 & segments[segment]))
        print "Intersection of Test2 with %s: %s" % (segment, len(test2 & segments[segment]))
        print "Intersection of Control1 with %s: %s" % (segment, len(contr1 & segments[segment]))
        print "Intersection of Control2 with %s: %s" % (segment, len(contr2 & segments[segment]))
    print "-------------------------------------------------------------------------"

print "DIVIDED BY LAST DIGIT IN USER_ID"

for c in sorted(camps):
    contr1 = set([x for x in control_camps[c] if x[:-1] < '5'])
    contr2 = control_camps[c] - contr1
    test1 = set([x for x in test_camps[c] if x[:-1] < '5'])
    test2 = test_camps[c] - test1
    print "For Campaign %s, Control1: %s, Control2: %s" % (c, len(contr1), len(contr2))
    print "For Campaign %s, Test1: %s, Test2: %s" % (c, len(test1), len(test2))
    for segment in sorted(segments):
        print "Intersection of Test1 with %s: %s" % (segment, len(test1 & segments[segment]))
        print "Intersection of Test2 with %s: %s" % (segment, len(test2 & segments[segment]))
        print "Intersection of Control1 with %s: %s" % (segment, len(contr1 & segments[segment]))
        print "Intersection of Control2 with %s: %s" % (segment, len(contr2 & segments[segment]))
    print "-------------------------------------------------------------------------"

