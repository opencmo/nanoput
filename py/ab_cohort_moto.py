import redis

r = redis.StrictRedis(host='segments.opendsp.com', port=6379, db=0)        

segments = ['archived:segment:363:fp:220','archived:segment:364:fp:220','archived:segment:365:fp:220','archived:segment:366:fp:220']

for ts1 in [1735, 1736, 1737, 1757, 1758, 1759]:
   for ts2 in [1735, 1736, 1737, 1757, 1758, 1759]:
      if ts2 <= ts1:
         continue
      for s1 in ['T', 'C']:
         for s2 in ['T', 'C']:
            for segment in segments:
               key1 = "ab_test2_ts_%s_%s" % (ts1, s1)
               key2 = "ab_test2_ts_%s_%s" % (ts2, s2)
               comp2_key = "ab_test2_ts_%s_%s_ts_%s_%s" % (ts1, s1, ts2, s2)
               comp3_key = "ab_test2_%s_ts_%s_%s_ts_%s_%s" % (segment, ts1, s1, ts2, s2)
               res1 = r.zinterstore(comp2_key, [key1, key2])
               print "Intersection of %s %s and %s %s: %s" % (ts1, s1, ts2, s2, res1)
               res2 = r.zinterstore(comp3_key, [comp2_key, segment])
               print "Intersection of %s %s and %s %s and segment %s: %s" % (ts1, s1, ts2, s2, segment, res2)
      print "---------------------------------------------"
