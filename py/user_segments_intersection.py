import os
import redis
import base64
import struct

r = redis.StrictRedis(host='segments.opendsp.com', port=6379, db=0)

def encode(s):
    try:
        s =s.replace(' ','+')
        cdec = base64.b64decode(s)
        s = struct.unpack("<IIII",cdec)
        uid = "%08X%08X%08X%08X" % s
        return uid
    except Exception, e:
        print "Error on %s: %s" % (s, e)
        return None
users = set(encode(line.strip()) for line in open('uniq_users.txt'))
print "Total correct unique users: %s" % len(users)
for segment in ['archived:segment:140:fp:180', 'archived:segment:139:fp:180', 'archived:segment:138:fp:180', 'archived:segment:137:fp:180', 'archived:segment:134:fp:180', 'archived:segment:242:fp:220', 'archived:segment:243:fp:220', 'archived:segment:244:fp:220', 'archived:segment:245:fp:220']:
    print "Segment %s total count: %s" % (segment, r.zcard(segment))

for segment in ['archived:segment:140:fp:180', 'archived:segment:139:fp:180', 'archived:segment:138:fp:180', 'archived:segment:137:fp:180', 'archived:segment:134:fp:180', 'archived:segment:242:fp:220', 'archived:segment:243:fp:220', 'archived:segment:244:fp:220', 'archived:segment:245:fp:220']:
    segs = set(r.zrange(segment, 0, -1))
    res = len(segs & users)
    if res:
        print "Intersection with segment %s: %s" % (segment, res)
    print '----------------------'
