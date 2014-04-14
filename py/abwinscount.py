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

camp = {
    '1638':'258',
    '1639':'258',
    '1640':'258',
    '1641':'258',
    '1642':'259',
    '1643':'259',
    '1644':'259',
    '1645':'259',
    '1651':'260',
    '1652':'260',
    '1653':'261',
    '1654':'261',
    '1655':'262',
    '1656':'262',
    '1657':'263',
    '1658':'263',
    '1659':'264',
    '1660':'264',
    '1663':'267',
    '1664':'267',
    '1678':'267',
    '1682':'267',
    '1665':'268',
    '1666':'268',
    '1679':'268',
    '1683':'268',
    '1667':'269',
    '1668':'269',
    '1680':'269',
    '1684':'269',
    '1669':'270',
    '1670':'270',
    '1681':'270',
    '1685':'270',
    '1671':'271',
    '1672':'271',
    '1673':'271',
    '1674':'271',
    '1675':'271',
    '1676':'271',
    '1677':'271'
}

imp = dict()
spend = dict()

r = redis.StrictRedis(host='segments.opendsp.com', port=6379, db=0)        

def read_file(k, t):
    # print "Calling read_file(%s, %s)" % (k.key,t)
    fname = '/opt/enr/log/processing/%s' % k.key.replace('/','_')
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
            if ts == '-' or price == 0.0 or ts not in camp:
                continue
            ts_key = "ab_test2_ts_%s_T" % (ts)
            c_key = "ab_test2_c_%s_T" % (camp[ts])
            #print user, ts, camp[ts]
            if r.zrank(ts_key, user) is not None:
                if ts not in imp:
                    imp[ts] = 1
                else: 
                    imp[ts] += 1
                if ts not in spend:
                    spend[ts] = price
                else:
                    spend[ts] += price
                #print ts, imp[ts], spend[ts], line[7], line[9]

            if r.zrank(c_key, user) is not None:
                if camp[ts] not in imp:
                    imp[camp[ts]] = 1
                else: 
                    imp[camp[ts]] += 1
                if camp[ts] not in spend:
                    spend[camp[ts]] = price
                else:
                    spend[camp[ts]] += price
                #print camp[ts], imp[camp[ts]], spend[camp[ts]], line[7], line[9]
               
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
                type_prefix = "%s/type=%s/win.i-74fa6add" % (hour_prefix, t)
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
