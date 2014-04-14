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
from boto.s3.key import Key
from common import *
import boto.dynamodb
import redis
import simplejson
import base64

now = int(time.time())

# This is the version of segment generator (should correspond to lua script)
_version = "v2"

# This is what we actually use
# version_prefix = "%s:"
version_prefix = ":"
   

def main():
    #region='us-east-1'
    region = 'ap-southeast-1'
    print 'Connecting to %s with IAM role' % (region)
    conn = boto.dynamodb.connect_to_region(region)
    print "Connection: %s" % conn
    table = conn.get_table('users1')
    skipped = 0
    newcnt = 0
    updatedcnt = 0
    samecnt = 0
    cnt = 0
    errcnt = 0


    for line in f:
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
        seg_list = ['%s:fp:1' % s for s in seg_list]
        try:
            item = table.get_item(hash_key=uid)
            json = item['doAttr']
            e = simplejson.loads(json)
            if not e:
                newcnt += 1
                e = []
        except boto.dynamodb.exceptions.DynamoDBKeyNotFoundError:
            newcnt += 1
            item = table.new_item(
                hash_key=uid,
                attrs={'dtAttr':'java.util.Set',
                       'doAttr':'[]'
                       }
                )
            e = []
        # e - existing
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
        item.put()
        cnt += 1
        if cnt % 1000 == 0:
            print item 
            print  "User count: %s total, updated %s, same %s, new %s, error %s"  % (cnt, updatedcnt,samecnt,newcnt,errcnt)
            print "Wrote %s users" % cnt
            item2 = table.new_item(
                hash_key='LAST_WRITE',
                    attrs={'dtAttr':'java.util.String',
                           'doAttr' : "LOTAME: User count: %s total, updated %s, same %s, new %s, error %s at %s"  % (cnt, updatedcnt,samecnt,newcnt,errcnt,datetime.datetime.now()),
                           'item' : item.__str__()
                           }
                )
            print item2
            item2.put()

    item2 = table.new_item(
                    hash_key='LAST_WRITE',
                    attrs={'dtAttr':'java.util.String',
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
