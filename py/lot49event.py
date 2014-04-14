#!/opt/enr/virtupy/bin/python
# $Id$
import base64
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

to_camps = {
    '1931':'353','1932':'354','1933':'355','1934':'356','1936':'357','1937':'358', '1938':'354', '1939':'353'
}

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days) + 1):
        yield start_date + datetime.timedelta(n)

def parse_date(datestring):
    return datetime.date(int(datestring[:4]), int(datestring[4:6]), int(datestring[6:8]))

def read_file(k, t):
    # print "Calling read_file(%s, %s)" % (k.key,t)
    fname = '/opt/enr/log/processing/%s' % k.key.replace('/','_')
    f = open(fname,'w')
    # print "Downloading %s to %s" % (k.key, fname)
    k.get_contents_to_file(f)
    f.close()
    g = gzip.GzipFile(fname)
    lines = g.readlines()
    line_cnt = 0
    for line in lines:
        line_cnt +=1
        line = line.strip()
        line = line.split("\t")
        if t == "abtestassignment":
            # TODO this is easily refactorable into metadata-driven code
            # taking logs structure from DB
            user = line[4]
            uts = long(line[1])
            type = line[5]
            if type == "C":
                c = line[6]
                c_status = line[7]
                c_redis_key = "ab_test2_c_%s_%s" % (c, c_status)
                c_T_redis_key = "ab_test2_c_%s_T" % (c)
                c_C_redis_key = "ab_test2_c_%s_C" % (c)
                c_N_redis_key = "ab_test2_c_%s_N" % (c)
                c_dirty_redis_key = "dirty_ab_test2_c_%s" % (c)
                if r.zrank(c_T_redis_key, user) is not None and c_status != "T":
                    r.zrem(c_T_redis_key, user)
                    r.zadd(c_dirty_redis_key, uts, user)
                elif r.zrank(c_C_redis_key, user) is not None and c_status != "C":
                    r.zrem(c_C_redis_key, user)
                    r.zadd(c_dirty_redis_key, uts, user)
                elif r.zrank(c_N_redis_key, user) is not None and c_status != "N":
                    r.zrem(c_N_redis_key, user)
                    r.zadd(c_dirty_redis_key, uts, user)
                elif r.zrank(c_dirty_redis_key, user) is None:
                    r.zadd(c_redis_key, uts, user)
            elif type == "TS":   
                ts = line[6]
                ts_status = line[7]
                ts_redis_key = "ab_test2_ts_%s_%s" % (ts, ts_status)
                ts_T_redis_key = "ab_test2_ts_%s_T" % (ts)
                ts_C_redis_key = "ab_test2_ts_%s_C" % (ts)
                ts_dirty_redis_key = "dirty_ab_test2_ts_%s" % (ts)
                c_dirty_redis_key = "dirty_ab_test2_c_%s" % (to_camps[ts])
                if r.zrank(c_dirty_redis_key, user) is not None:
                    r.zrem(ts_T_redis_key, user)
                    r.zrem(ts_C_redis_key, user)
                    r.zadd(ts_dirty_redis_key, uts, user)
                elif r.zrank(ts_T_redis_key, user) is not None and ts_status != "T":
                    r.zrem(ts_T_redis_key, user)
                    r.zadd(ts_dirty_redis_key, uts, user)
                elif r.zrank(ts_C_redis_key, user) is not None and ts_status != "C":
                    r.zrem(ts_C_redis_key, user)
                    r.zadd(ts_dirty_redis_key, uts, user)
                elif r.zrank(ts_dirty_redis_key, user) is None:
                    r.zadd(ts_redis_key, uts, user)
               
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
        before_yesterday = dt - datetime.timedelta(days=2)
        dayrange = [(before_yesterday.year, before_yesterday. month, before_yesterday.day), (yesterday.year, yesterday. month, yesterday.day)]
        days = [(year, "0%s" % month if month < 10 else month, "0%s" % day if day < 10 else day) for (year, month, day) in dayrange]
        
    d = parse_creds(CRED_FILE)
    conn = S3Connection(d['akey'], d['skey'])

    cnt = 0
    line_cnt = 0
    bucket = conn.get_bucket("stats-new.opendsp.com")
    # TODO Maybe make this doing things by hour
    for (year, month, day) in days:
        day_prefix = "year=%s/month=%s/day=%s" % (year, month, day)
        print "Reading data for %s" % day_prefix

        for hour in range(0,24):
            if hour < 10:
                hour = "0%s" % hour
            hour_prefix = "%s/hour=%s" % (day_prefix, hour)
            # print "Reading data for %s" % hour_prefix
            for t in ["abtestassignment"]: # ignore click for now,"click"]:
                type_prefix = "%s/type=%s/" % (hour_prefix, t)
                # print "Reading data for %s (%s)" % (type_prefix, t)
                rs = bucket.list(prefix=type_prefix)
                for k in rs:
                    # print "Key: %s" % k.key
                    line_cnt += read_file(k, t)
                    cnt += 1
                    if cnt % 1000 == 0:
                        print "Processed %s files, currently at %s" % (cnt, k.key)
                        print "Processed %s files for total of %s records" % (cnt, line_cnt)
