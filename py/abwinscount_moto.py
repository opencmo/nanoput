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
status_camps = dict()
for c in camps:
    test = set()
    control = set()
    for ts in camps[c]:
        test = test | set(r.zrange("ab_test2_ts_%s_T" % (ts), 0, -1))
        control = control | set(r.zrange("ab_test2_ts_%s_C" % (ts), 0, -1))
    control = control - test
    status_camps[c] = {'T':test, 'C':control}
    
    print "For campaign %s in Test: %s" % (c, len(test))
    print "For campaign %s in Control: %s" % (c, len(control))

imp = dict()
spend = dict()

def read_file(k, t):
    # print "Calling read_file(%s, %s)" % (k.key,t)
    fname = '/ebs3/boba/wins/%s' % k.key.replace('/','_')
    f = open(fname,'w')
    # print "Downloading %s to %s" % (k.key, fname)
    k.get_contents_to_file(f)
    f.close()
    g = gzip.GzipFile(fname)
    lines = g.readlines()
    # print len(lines)
    line_cnt = 0
    for line in lines:
        line_cnt +=1
        line = line.strip()
        line = line.split("\t")
        if t == "win":
            # TODO this is easily refactorable into metadata-driven code
            # taking logs structure from DB
            user = line[32]
            ts = line[5]
            price = float(line[8])
            if ts == '-' or price == 0.0 or ts not in to_camps:
                continue
            ts_key = "ab_test2_ts_%s_T" % (ts)
            #print user, ts, camp[ts]
            if r.zrank(ts_key, user) is not None:
                if to_camps[ts] not in imp:
                    imp[to_camps[ts]] = 1
                else: 
                    imp[to_camps[ts]] += 1
                if to_camps[ts] not in spend:
                    spend[to_camps[ts]] = price
                else:
                    spend[to_camps[ts]] += price
                #print ts, imp[ts], spend[ts], line[7], line[9]
               
    return line_cnt

if __name__ == "__main__":
    if len(sys.argv) == 4:
        year = sys.argv[1]
        month = sys.argv[2]
        day = sys.argv[3]
        if "-" in day:
            (df,dt) = day.split("-")
            dayrange = range(int(df),int(dt)+1)
            days = [(year, month, "0%s" % d if d < 10 else d) for d in dayrange]
    else:
        dt = datetime.datetime.now()
        yesterday = dt - datetime.timedelta(days=1)
        dayrange = [(yesterday.year, yesterday. month, yesterday.day), (dt.year, dt.month, dt.day)]
        days = [(year, "0%s" % month if month < 10 else month, "0%s" % day if day < 10 else day) for (year, month, day) in dayrange]
        
    d = parse_creds(CRED_FILE)
    conn = S3Connection(d['akey'], d['skey'])

    cnt = 0
    line_cnt = 0
    bucket = conn.get_bucket("stats.opendsp.com")
    # TODO Maybe make this doing things by hour
    for (year, month, day) in days:
        day_prefix = "year=%s/month=%s/day=%s" % (year, month, day)
        print "Reading data for %s" % day_prefix

        for hour in range(0,24):
            if hour < 10:
                hour = "0%s" % hour
            hour_prefix = "%s/hour=%s" % (day_prefix, hour)
            # print "Reading data for %s" % hour_prefix
            for t in ["win"]: # ignore click for now,"click"]:
                type_prefix = "%s/type=%s/win" % (hour_prefix, t)
                # print "Reading data for %s (%s)" % (type_prefix, t)
                rs = bucket.list(prefix=type_prefix)
                for k in rs:
                    # print "Key: %s" % k.key
                    line_cnt += read_file(k, t)
                    cnt += 1
                    if cnt % 1000 == 0:
                        print "Processed %s files, currently at %s" % (cnt, k.key)
                        print "Processed %s files for total of %s records" % (cnt, line_cnt)
    print imp
    print spend
