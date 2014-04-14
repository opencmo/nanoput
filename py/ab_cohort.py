import redis

r = redis.StrictRedis(host='segments.opendsp.com', port=6379, db=0)        

segment = 'archived:segment:138:fp:180'

for ts1 in [1640, 1644]:
   for ts2 in [1638, 1639, 1640, 1641, 1642, 1643, 1645]:
      for s1 in ['T', 'C']:
         for s2 in ['T', 'C']:
            key1 = "ab_test2_ts_%s_%s" % (ts1, s1)
            key2 = "ab_test2_ts_%s_%s" % (ts2, s2)
            comp2_key = "ab_test2_ts_%s_%s_ts_%s_%s" % (ts1, s1, ts2, s2)
            comp3_key = "ab_test2_%s_ts_%s_%s_ts_%s_%s" % (segment, ts1, s1, ts2, s2)
            res1 = r.zinterstore(comp2_key, [key1, key2])
            print "Intersection of %s %s and %s %s: %s" % (ts1, s1, ts2, s2, res1)
            res2 = r.zinterstore(comp3_key, [comp2_key, segment])
            print "Intersection of %s %s and %s %s and segment %s: %s" % (ts1, s1, ts2, s2, segment, res2)
      print "---------------------------------------------"
   for c in [258, 259]:
      for s1 in ['T', 'C']:
         for s2 in ['T', 'C']:
            key1 = "ab_test2_ts_%s_%s" % (ts1, s1)
            key2 = "ab_test2_c_%s_%s" % (c, s2)
            comp2_key = "ab_test2_ts_%s_%s_c_%s_%s" % (ts1, s1, c, s2)
            comp3_key = "ab_test2_%s_ts_%s_%s_c_%s_%s" % (segment, ts1, s1, c, s2)
            res1 = r.zinterstore(comp2_key, [key1, key2])
            print "Intersection of %s %s and %s %s: %s" % (ts1, s1, c, s2, res1)
            res2 = r.zinterstore(comp3_key, [comp2_key, segment])
            print "Intersection of %s %s and %s %s and segment %s: %s" % (ts1, s1, c, s2, segment, res2)
      print "---------------------------------------------"