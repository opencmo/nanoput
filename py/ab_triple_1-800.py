import redis

r = redis.StrictRedis(host='segments.opendsp.com', port=6379, db=0)        

campaigns = sorted({'294', '295'})

tss = sorted({'1785', '1786', '1787', '1788', '1789', '1790', '1791', '1792', '1793', '1794', '1795', '1796', '1797', '1798'})

segments = sorted({'archived:segment:117:fp:180', 'archived:segment:118:fp:180', 'archived:segment:119:fp:180', 'archived:segment:120:fp:180',
                   'archived:segment:121:fp:180', 'archived:segment:122:fp:180', 'archived:segment:123:fp:180'})

mes_segments = sorted({'archived:segment:134:fp:180', 'archived:segment:137:fp:180', 'archived:segment:138:fp:180',
                              'archived:segment:139:fp:180', 'archived:segment:140:fp:180'})

statuses = ['T', 'C']

seg_sets = dict()
mes_seg_sets = dict()

for s in segments:
   seg_sets[s] = set(r.zrange(s, 0, -1))
for s in mes_segments:
   mes_seg_sets[s] = set(r.zrange(s, 0, -1))

for c in campaigns:
   for status in statuses:
      key = "ab_test2_c_%s_%s" % (c, status)
      st_set = set(r.zrange(key, 0, -1))
      print "Size of %s for Campaign %s: %s" % (status, c, len(st_set))
      for seg in segments:
         print "Intersection of %s with %s for Campaign %s: %s" % (seg, status, c, len(st_set & seg_sets[seg]))
         for mes_seg in mes_segments:
            print "Intersection of %s with %s with %s for Campaign %s: %s" % (seg, mes_seg, status, c, len(st_set & seg_sets[seg] & mes_seg_sets[mes_seg]))
      print "---------------------------------------------"
print
for ts in tss:
   for status in statuses:
      key = "ab_test2_ts_%s_%s" % (ts, status)
      st_set = set(r.zrange(key, 0, -1))
      print "Size of %s for TS %s: %s" % (status, ts, len(st_set))
      for seg in segments:
         print "Intersection of %s with %s for TS %s: %s" % (seg, status, ts, len(st_set & seg_sets[seg]))
         for mes_seg in mes_segments:
            print "Intersection of %s with %s with %s for TS %s: %s" % (seg, mes_seg, status, ts, len(st_set & seg_sets[seg] & mes_seg_sets[mes_seg]))
      print "---------------------------------------------"
         