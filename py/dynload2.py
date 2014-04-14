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

now = int(time.time())

# This is the version of segment generator (should correspond to lua script)
_version = "v2"

# This is what we actually use
# version_prefix = "%s:"
version_prefix = ":"

def delete_older_than(key, delta):
    then = now - delta
    print 'Total users: %s' % (r.zcard(key))
    old = r.zrevrangebyscore(key, then, '-inf')
    print "Entries older than %s seconds: %s" % (delta, len(old))
    cur = r.zrevrangebyscore(key, now, then)
    print "Current entries: %s" % (len(cur))
    removed = r.zremrangebyscore(key, '-inf', then)
    print "Removed: %s" % removed
    return cur
    

def main():
    if (len(sys.argv)) == 1:
        period = 'hourly'
    else:
        period = sys.argv[1]
    if period not in ['hourly','daily']:
        print 'Wrong period'
        os.exit()
    print "Doing %s" % period
    hourly = period == 'hourly'
    inst_id = get_instance_id()
    d = parse_creds(CRED_FILE)
    global r
    r = redis.StrictRedis(host='user10.va.opendsp.com', port=6379, db=0)
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
        if hourly:
            delta = 3600
        else:
            # Monthly deletion
            delta = 3600*24*30
        cur = delete_older_than(seg, delta)
        for user in cur:
            if user.startswith('odsp='):
                user = user[5:]
            if user not in users:
                users[user] = sets.Set()
            users[user].add(seg_id)
            # print "archived:%s %s %s" % (seg, now, user)
            r.zadd("archived:%s" % seg, now, user)
    
    for region in ['us-east-1']:#,
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
        cnt = 0
        for user in users:
            try:
                item = table.get_item(hash_key=user)
                json = item['doAttr']
                e = simplejson.loads(json)
                if not e:
                    newcnt += 1
                    e = []
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
            
            item['doAttr'] = simplejson.dumps(n)
            #print "Putting %s" % item
            item.put()
            cnt += 1
            if cnt % 50 == 0:
                print item 
                print  "User count: %s total, updated %s, same %s, new %s"  % (cnt, updatedcnt,samecnt,newcnt)
                print "Wrote %s users" % cnt
        item = table.new_item(
                    hash_key='LAST_WRITE',
                    attrs={'dtAttr':'java.util.String',
                           'doAttr' : "User count: %s total, updated %s, same %s, new %s at %s"  % (cnt, updatedcnt,samecnt,newcnt,datetime.datetime.now())
                           }
                    )
        print item
        item.put()

        print "Added or updated %s users, skipped %s, to %s region" % (cnt, skipped, region)



if __name__ == "__main__":
    main()
    print '========================================================'
    print 
