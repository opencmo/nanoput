import os
import redis
import base64
import struct
import random
import gzip
import time
import httplib
import socket

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from common import *

r = redis.StrictRedis(host='segments.opendsp.com', port=6379, db=0)

def encode(s):
    try:
        s =s.replace(' ','+')
        cdec = base64.b64decode(s)
        s = struct.unpack("<IIII",cdec)
        uid = "%08X%08X%08X%08X" % s
        return uid
    except Exception, e:
        #print "Error on %s: %s" % (s, e)
        return None

adx_count_dict = {}
pub_count_dict = {}
union_set = set()
for segment in ['archived:segment:140:fp:180', 'archived:segment:139:fp:180', 'archived:segment:138:fp:180', 'archived:segment:137:fp:180', 'archived:segment:134:fp:180', 'archived:segment:242:fp:220', 'archived:segment:243:fp:220', 'archived:segment:244:fp:220', 'archived:segment:245:fp:220']:
    segs = set(r.zrange(segment, 0, -1))
    print "Segment %s total count: %s" % (segment, len(segs))
    l_segs = list(segs)
    adx_count_dict[segment] = dict([(l_segs[i],0) for i in sorted(random.sample(xrange(len(l_segs)), 100))])
    pub_count_dict[segment] = dict(adx_count_dict[segment])
    union_set = union_set | set(adx_count_dict[segment].keys())

print "Union set contains: %s" % (len(union_set))
d = parse_creds(CRED_FILE)
conn = S3Connection(d['akey'], d['skey'])
bucket = conn.get_bucket("stats.opendsp.com")
for day in [19,20]:
    day_prefix = "year=2015/month=12/day=%s" % (day)
    for hour in range(0,24):
        print "Hour: %s" % (hour)
        if hour < 10:
            hour = "0%s" % hour
        full_prefix = "%s/hour=%s/type=request/" % (day_prefix, hour)
        rs = bucket.list(prefix=full_prefix)
        for k in rs:
            fname = '/ebs3/boba/tmp_file'
            for i in xrange(10):
                try:
                    k.get_contents_to_filename(fname)
                except:
                    if i == 9:
                        raise
                    time.sleep(1500)
                    continue
            g = gzip.GzipFile(fname)
            try:
                lines = g.readlines()
            except:
                print "Corrupted file %s" % (fname)
                continue
            #print "Lines read %s" % (len(lines))
            for line in lines:
                line = line.strip()
                line = line.split("\t")
                if line[3] == "adx" or line[3] == "pubmatic":
                    user = encode(line[6])
                    if user is not None and user in union_set:
                        for segment in ['archived:segment:140:fp:180', 'archived:segment:139:fp:180', 'archived:segment:138:fp:180', 'archived:segment:137:fp:180', 'archived:segment:134:fp:180', 'archived:segment:242:fp:220', 'archived:segment:243:fp:220', 'archived:segment:244:fp:220', 'archived:segment:245:fp:220']:
                            if line[3] == "adx" and user in adx_count_dict[segment]:
                                adx_count_dict[segment][user] += 1
                            if line[3] == "pubmatic" and user in pub_count_dict[segment]:
                                pub_count_dict[segment][user] += 1
            g.close()
        adx_outname = "/ebs3/boba/adxoutfile%s%s.txt" % (day, hour)
        pub_outname = "/ebs3/boba/puboutfile%s%s.txt" % (day, hour)
        adx = open(adx_outname, 'w')
        pub = open(pub_outname, 'w')
        for segment in ['archived:segment:140:fp:180', 'archived:segment:139:fp:180', 'archived:segment:138:fp:180', 'archived:segment:137:fp:180', 'archived:segment:134:fp:180', 'archived:segment:242:fp:220', 'archived:segment:243:fp:220', 'archived:segment:244:fp:220', 'archived:segment:245:fp:220']:
            adx.write("Segment %s\n" % (segment))
            pub.write("Segment %s\n" % (segment))
            users = adx_count_dict[segment]
            for c in sorted(users, key=users.get, reverse=True):
                adx.write("%s, %s\n" % (c, users[c]))
            users = pub_count_dict[segment]
            for c in sorted(users, key=users.get, reverse=True):
                pub.write("%s, %s\n" % (c, users[c]))
            adx.write("-------------------------------\n")
            pub.write("-------------------------------\n")
        adx.close()
        pub.close()
