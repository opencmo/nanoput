#!/opt/enr/virtupy/bin/python
# $Id$
import struct
import sets
import sys
import os
import subprocess
import time
import datetime
from boto.s3.connection import S3Connection
from boto.dynamodb2.table import Table
from boto.s3.key import Key
from common import *
import boto.dynamodb2
import redis
import simplejson
import base64

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
   
BATCH_SIZE=24

def main():
    aud = sys.argv[1]
    f = open(aud)
    region='us-east-1'
    #region = 'ap-southeast-1'
    print 'Connecting to %s with IAM role' % (region)
    #conn = boto.dynamodb.connect_to_region(region)

#    table = conn.get_table('users1')
    table = Table('users1')
    skipped = 0
    newcnt = 0
    updatedcnt = 0
    samecnt = 0
    cnt = 0
    batchcnt = 0
    errcnt = 0
    batch = None
    

    for line in f:
        
        if not batch:
            batch = table.batch_write()
            print "Got batch %s" % batch
    
        (cookie,segs) = line.split("\t")
        if " " in cookie:
            cookie = cookie.replace(" ","+")
        if not cookie.endswith("=="):
            cookie = cookie + "=="
        try:
            # print "Decoding %s" % cookie
            cdec = base64.b64decode(cookie)
            s = struct.unpack("<IIII",cdec)
            uid = "%08X%08X%08X%08X" % s
        except:
            errcnt+=1
            continue

        # print "%s -> %s" % (cookie, uid)
        seg_list = segs.split(",")
        seg_list = ['%s:tp:1' % s for s in seg_list]
        try:
            item = table.get_item(key=uid)
            json = item['doAttr']
            e = simplejson.loads(json)
            if not e:
                newcnt += 1
                e = []
        except boto.dynamodb2.exceptions.ItemNotFound:
            newcnt += 1
            item = {'dtAttr':'java.util.Set',
                    'doAttr':'[]'
                       }
            e = []
        # e - existing
        e = [s.replace(':fp:',':tp:').strip() for s in e]
        e = sets.Set(e)
        # n - new
        n = sets.Set(seg_list)
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
        batchcnt+=1
        batch.put_item(data={'doAttr':item['doAttr'],
                             'dtAttr':'java.util.Set',
                             'key' :uid})
                             
        #item.put()
        cnt += 1
        if cnt % BATCH_SIZE == 0:
            batch.flush()
            batch = None
        if cnt % 5000 == 0:
            print "OK"
            print item 
            print  "User count: %s total, updated %s, same %s, new %s, error %s"  % (cnt, updatedcnt,samecnt,newcnt,errcnt)
            print "Wrote %s users" % cnt
            item2 = table.new_item(
                key='LAST_WRITE',
                    attrs={'dtAttr':'java.lang.String',
                           'doAttr' : "LOTAME: User count: %s total, updated %s, same %s, new %s, error %s at %s\nLast user: %s : %s"  % (cnt, updatedcnt,samecnt,newcnt,errcnt,datetime.datetime.now(), user, str(item))
                           }
                )
            print item2
            item2.put()
    batch.flush()
    item2 = table.new_item(
                    {key:'LAST_WRITE',
                    'dtAttr':'java.util.String',
                    'doAttr' : "LOTAME: User count: %s total, updated %s, same %s, new %s, error %s at %s"  % (cnt, updatedcnt,samecnt,newcnt,errcnt,datetime.datetime.now()),
                     'item' : item
                           }
                    )
    print item2
    item2.put()
    print "Added or updated %s users, skipped %s, to %s region" % (cnt, skipped, region)

if __name__ == "__main__":
    main()
    print '========================================================'
    print 
