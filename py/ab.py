#!/opt/enr/virtupy/bin/python
# $Id$
import sets
import sys
import os
import subprocess
import time
import datetime
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from common import *
import boto.dynamodb
import redis
import simplejson

"""
Same as dynload but for 

"""

now = int(time.time())

# This is the version of segment generator (should correspond to lua script)
_version = "v2"

# This is what we actually use
# version_prefix = "%s:"
version_prefix = ":"

def process_older_than(key, delta, remove=True):
    then = now - delta
    print 'Total users: %s' % (r.zcard(key))
    old = r.zrevrangebyscore(key, then, '-inf')
    print "Entries older than %s seconds: %s" % (delta, len(old))
    cur = r.zrevrangebyscore(key, now, then)
    print "Current entries: %s" % (len(cur))
    if remove:
        removed = r.zremrangebyscore(key, '-inf', then)
        print "Removed: %s" % removed
    return cur
    

def main():
    if (len(sys.argv)) == 1:
        period = 'hourly'
    else:
        period = sys.argv[1]
    if len(sys.argv) > 2:
       regions = sys.argv[2:]
    else:
       regions = ['us-east-1']
    print 'Pushing to regions: %s' % regions
    if period not in ['hourly','daily']:
        print 'Wrong period'
        os.exit()
    print "dynload start: %s" % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print "Doing %s" % period
    hourly = period == 'hourly'
    inst_id = get_instance_id()
    d = parse_creds(CRED_FILE)
    global r
    r = redis.StrictRedis(host='segments.opendsp.com', port=6379, db=0)
    print 'Connected to Redis'

    if hourly:
        prefix = "segment%s" % version_prefix
    else:
        prefix = "archived:segment%s" % version_prefix
    keys = "%s*" % prefix
    print "Listing keys: %s" % keys
    seg_keys = r.keys(keys)
    print "Found %s segments: %s" % (len(seg_keys), seg_keys)
    users = {}

    for seg in seg_keys:
        seg_id = seg.replace(prefix,'')
        print 'Processing %s' % seg
        # Just info
        delta = 3600*24
        process_older_than(seg,delta,False)
        print '-------------------------------'
        if hourly:
            delta = 3600
        else:
            # Monthly deletion
            delta = 3600*24*30
        cur = process_older_than(seg, delta, True)
        print "%s users in %s" % (len(cur), seg)
        for user in cur:
            if user[4] == '=':
                user = user[5:]
            if user not in users:
                users[user] = sets.Set()
            users[user].add(seg_id)
            # print "archived:%s %s %s" % (seg, now, user)
            if hourly:
                r.zadd("archived:%s" % seg, now, user)
    
    for region in regions:
        print 'Connecting to %s with IAM role' % (region)
        conn = boto.dynamodb.connect_to_region(region)
        
        #conn = boto.dynamodb.connect_to_region(region,
        #    aws_access_key_id=d['akey'],
        #    aws_secret_access_key=d['skey'])
        print "Connection: %s" % conn
        table = conn.get_table('users1')
        skipped = 0
        newcnt = 0
        updatedcnt = 0
        samecnt = 0
        malformed_cnt = 0
        cnt = 0
        for user in users:
            try:
                item = table.get_item(hash_key=user)
                json = item['doAttr']
                try:
                    e = simplejson.loads(json)
                    if not e:
                        newcnt += 1
                        e = []
                except simplejson.scanner.JSONDecodeError, err1:
                    print "Malformed JSON: %s...: %s, will try again replacing ' with \"" % (json[0:40], err1)
                    try:
                        json = json.replace("'",'"')
                        e = simplejson.loads(json)
                    except simplejson.scanner.JSONDecodeError, err2:
                        print "Malformed JSON: %s...: %s" % (json, err2)
                        e = []
                        malformed_cnt += 1
            except boto.dynamodb.exceptions.DynamoDBKeyNotFoundError:
                newcnt += 1
                item = table.new_item(
                    hash_key=user,
                    attrs={'dtAttr':'java.util.Set',
                           'doAttr':'[]'
                           }
                    )
                e = []
            # e - existing
            e = sets.Set(e)
            # n - new
            n = users[user]
            # combine
            n.update(e)
            # if the same no need to write
            if n == e:
                samecnt += 1
                skipped += 1
                continue
            elif e:
                updatedcnt += 1
            n = list(n)
            
            lastUser = item['doAttr'] = simplejson.dumps(n)
            #print "Putting %s" % item
            item.put()
            cnt += 1
            if cnt % 1000 == 0:
                print item 
                print  "User count: %s total, updated %s, same %s, new %s, malformed and replaced %s"  % (cnt, updatedcnt,samecnt,newcnt, malformed_cnt)
                print "Wrote %s users" % cnt
            item = table.new_item(
                    hash_key='LAST_WRITE',
                    attrs={'dtAttr':'java.util.String',
                           'doAttr' : "%s User count: %s total, updated %s, same %s, new %s, malformed and replaced %s, at %s\nLast user: %s: %s"  % (period, cnt, updatedcnt,samecnt,newcnt,malformed_cnt, datetime.datetime.now(),user, lastUser)
                           }
                    )
            print item
            item.put()

        print "Added or updated %s users, skipped %s, to %s region" % (cnt, skipped, region)
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        r.sadd("last_write_%s" % period, dt)
        print "Dynload end for %s: %s" % (region, dt)


if __name__ == "__main__":
    main()
    print '========================================================'
    print 
